# `frontend/` — Next.js app

Next.js (App Router) + React + TypeScript + Tailwind. Server-rendered pages that
call the FastAPI backend, with client "islands" for the interactive tools.
Built as `output: "standalone"` so the Docker image ships a self-contained
`.next/standalone` server with no `node_modules`.

## Two backend URLs (important)

`lib/api.ts` resolves the API base per environment:

- **Browser** → `NEXT_PUBLIC_API_BASE_URL` (baked at build time; the host-published
  backend port). Defaults to `http://127.0.0.1:8000` — the explicit IPv4 loopback,
  *not* `localhost`, because on Windows Node resolves `localhost` to IPv6 first
  while Uvicorn binds IPv4 only (multi-second SSR stalls otherwise).
- **Server / SSR** → `API_INTERNAL_BASE_URL` when set. Inside docker-compose this
  is `http://backend:8000` (the compose service name); `localhost` there would
  point the frontend container at itself.

## Layout

| Path | What's in it |
|---|---|
| `app/` | Route segments (one folder per page) + `layout.tsx` + `globals.css`. See `app/explanation.md`. |
| `components/` | Reusable UI + the interactive client islands (price check, autocomplete, gauges, estimators). See `components/explanation.md`. |
| `lib/` | API client, i18n, React contexts (auth / language / preferences), formatting, local history. See `lib/explanation.md`. |
| `public/` | Static assets. |

## i18n

8 languages (`en, hi, ta, te, bn, mr, gu, kn`), autonym labels. Current language
lives in the `sahaj_lang` cookie, read server-side in `layout.tsx` via
`parseLang`, and switched client-side through `lib/language-context.tsx`.

## Commands

```
npm run dev        # dev server on :3000
npm run typecheck  # tsc --noEmit  (also aliased as `npm run lint`)
npm run build      # production build (CI runs this)
```
