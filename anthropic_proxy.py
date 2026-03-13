from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import httpx
import json
import uuid

VLLM_URL = "https://vllm.3dinteractive.cloud/v1"
MODEL = "/models/qwen35"

app = FastAPI()


def extract_text(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for c in content:
            if isinstance(c, dict):
                if c.get("type") == "text":
                    parts.append(c.get("text", ""))
                elif c.get("type") == "tool_result":
                    result_content = c.get("content", "")
                    if isinstance(result_content, list):
                        result_content = " ".join(
                            r.get("text", "") for r in result_content if isinstance(r, dict)
                        )
                    parts.append(f"[Tool result: {result_content}]")
        return "".join(parts)
    return ""


def openai_tool_calls_to_claude(tool_calls):
    content = []
    for tc in tool_calls:
        fn = tc.get("function", {})
        try:
            arguments = json.loads(fn.get("arguments", "{}"))
        except json.JSONDecodeError:
            arguments = {}
        content.append({
            "type": "tool_use",
            "id": tc.get("id", f"tool_{uuid.uuid4().hex[:8]}"),
            "name": fn.get("name", ""),
            "input": arguments,
        })
    return content


def messages_claude_to_openai(claude_messages, system_prompt=None):
    openai_messages = []

    if system_prompt:
        openai_messages.append({"role": "system", "content": system_prompt})

    for m in claude_messages:
        role = m.get("role")
        content = m.get("content")

        if role == "assistant":
            if isinstance(content, list):
                text_parts = [c.get("text", "") for c in content if isinstance(c, dict) and c.get("type") == "text"]
                tool_uses = [c for c in content if isinstance(c, dict) and c.get("type") == "tool_use"]
                msg = {"role": "assistant", "content": "".join(text_parts) or None}
                if tool_uses:
                    msg["tool_calls"] = [
                        {
                            "id": tu["id"],
                            "type": "function",
                            "function": {
                                "name": tu["name"],
                                "arguments": json.dumps(tu.get("input", {})),
                            }
                        }
                        for tu in tool_uses
                    ]
                openai_messages.append(msg)
            else:
                openai_messages.append({"role": "assistant", "content": extract_text(content)})

        elif role == "user":
            if isinstance(content, list):
                tool_results = [c for c in content if isinstance(c, dict) and c.get("type") == "tool_result"]
                text_parts = [c for c in content if isinstance(c, dict) and c.get("type") != "tool_result"]

                for tr in tool_results:
                    result_content = tr.get("content", "")
                    if isinstance(result_content, list):
                        result_content = " ".join(
                            r.get("text", "") for r in result_content if isinstance(r, dict)
                        )
                    openai_messages.append({
                        "role": "tool",
                        "tool_call_id": tr.get("tool_use_id", ""),
                        "content": result_content,
                    })

                if text_parts:
                    text = "".join(c.get("text", "") for c in text_parts if isinstance(c, dict))
                    if text.strip():
                        openai_messages.append({"role": "user", "content": text})
            else:
                openai_messages.append({"role": "user", "content": extract_text(content)})
        else:
            openai_messages.append({"role": role, "content": extract_text(content)})

    return openai_messages


def build_tool_system_prompt(claude_tools):
    tools_json = json.dumps(claude_tools, indent=2)
    return f"""You have access to the following tools. When you need to use a tool, respond with ONLY a JSON object in this exact format and nothing else:
{{"type": "tool_use", "id": "tool_1", "name": "<tool_name>", "input": {{<arguments>}}}}

Rules:
- If using a tool, output ONLY the raw JSON object — no markdown, no explanation, no code fences.
- If you do not need a tool, respond normally in plain text.
- Do not mix tool JSON and regular text in the same response.

Available tools:
{tools_json}"""


def try_parse_tool_call(text):
    """Try to extract a tool_use JSON object from the model's response."""
    stripped = text.strip()

    # Strip markdown code fences if present
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        stripped = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:]).strip()

    if not stripped.startswith("{"):
        return None

    try:
        parsed = json.loads(stripped)
        if parsed.get("type") == "tool_use" and "name" in parsed:
            return {
                "type": "tool_use",
                "id": parsed.get("id", f"tool_{uuid.uuid4().hex[:8]}"),
                "name": parsed["name"],
                "input": parsed.get("input", {}),
            }
    except json.JSONDecodeError:
        pass

    return None


@app.post("/v1/messages")
async def messages(request: Request):
    try:
        body = await request.json()
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": f"Invalid JSON body: {e}"})

    try:
        # Extract system prompt
        system_prompt = None
        raw_system = body.get("system")
        if isinstance(raw_system, str):
            system_prompt = raw_system
        elif isinstance(raw_system, list):
            system_prompt = " ".join(
                s.get("text", "") for s in raw_system if isinstance(s, dict) and s.get("type") == "text"
            )

        openai_messages = messages_claude_to_openai(body.get("messages", []), system_prompt)

        # Inject tools as system prompt if present (vLLM doesn't support native tool calling without flags)
        claude_tools = body.get("tools")
        if claude_tools:
            tool_system = build_tool_system_prompt(claude_tools)
            if openai_messages and openai_messages[0]["role"] == "system":
                openai_messages[0]["content"] += "\n\n" + tool_system
            else:
                openai_messages.insert(0, {"role": "system", "content": tool_system})

        payload = {
            "model": MODEL,
            "messages": openai_messages,
            "max_tokens": body.get("max_tokens", 1024),
            "temperature": body.get("temperature", 0.7),
        }

        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(f"{VLLM_URL}/chat/completions", json=payload)
            resp.raise_for_status()

        data = resp.json()
        choice = data["choices"][0]
        message = choice["message"]
        finish_reason = choice.get("finish_reason", "stop")

        content_blocks = []
        stop_reason = "end_turn"

        if finish_reason == "length":
            stop_reason = "max_tokens"

        raw_text = message.get("content", "") or ""

        # If tools were available, try to parse a tool call from the response
        if claude_tools:
            tool_block = try_parse_tool_call(raw_text)
            if tool_block:
                content_blocks.append(tool_block)
                stop_reason = "tool_use"
            elif raw_text:
                content_blocks.append({"type": "text", "text": raw_text})
        else:
            # Also handle native tool_calls if vLLM ever returns them
            if message.get("tool_calls"):
                content_blocks.extend(openai_tool_calls_to_claude(message["tool_calls"]))
                stop_reason = "tool_use"
            elif raw_text:
                content_blocks.append({"type": "text", "text": raw_text})

        usage = data.get("usage", {})

        return {
            "id": data.get("id", f"msg_{uuid.uuid4().hex}"),
            "type": "message",
            "role": "assistant",
            "content": content_blocks,
            "model": MODEL,
            "stop_reason": stop_reason,
            "stop_sequence": None,
            "usage": {
                "input_tokens": usage.get("prompt_tokens", 0),
                "output_tokens": usage.get("completion_tokens", 0),
            },
        }

    except httpx.HTTPStatusError as e:
        return JSONResponse(
            status_code=502,
            content={"error": f"vLLM returned {e.response.status_code}", "detail": e.response.text}
        )
    except Exception as e:
        import traceback
        return JSONResponse(
            status_code=500,
            content={"error": str(e), "traceback": traceback.format_exc()}
        )