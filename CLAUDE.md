# Project: ai_3dinteractive

A React + TypeScript + Vite web application for 3D Interactive AI content/learning platform.

## Tech Stack
- React 19, TypeScript, Vite 7
- Tailwind CSS v4 (via @tailwindcss/vite)
- React Router v7
- Zustand for state management
- Lucide React for icons

## Project Structure
- `src/App.tsx` - Root component
- `src/pages/` - Page components
- `src/components/` - Reusable components
- `src/data/` - Data files (e.g., aiData.ts for AI content)
- `src/zustand/` - Zustand stores

## Commands
- `npm run dev` - Start dev server
- `npm run build` - TypeScript check + Vite build
- `npm run lint` - ESLint
- `npm run preview` - Preview production build

## Conventions
- Use TypeScript strictly
- Tailwind CSS for all styling (no CSS modules or inline styles unless necessary)
- Zustand for global state
- React Router v7 for navigation
