from fastapi import FastAPI, Request
import httpx

VLLM_URL = "https://vllm.3dinteractive.cloud/v1"
MODEL = "/models/qwen35"

app = FastAPI()

def extract_text(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join([c.get("text", "") for c in content if isinstance(c, dict)])
    return ""

@app.post("/v1/messages")
async def messages(request: Request):
    body = await request.json()

    messages = []
    for m in body.get("messages", []):
        messages.append({
            "role": m.get("role"),
            "content": extract_text(m.get("content"))
        })

    payload = {
        "model": MODEL,
        "messages": messages,
        "max_tokens": body.get("max_tokens", 1024),
        "temperature": body.get("temperature", 0.7)
    }

    async with httpx.AsyncClient(timeout=120) as client:
        resp = await client.post(
            f"{VLLM_URL}/chat/completions",
            json=payload
        )

    data = resp.json()

    text = data["choices"][0]["message"]["content"]

    return {
        "id": "msg_proxy",
        "type": "message",
        "role": "assistant",
        "content": [
            {
                "type": "text",
                "text": text
            }
        ]
    }