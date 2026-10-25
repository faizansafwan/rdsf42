# UK Day-Ahead Wind Forecast Dashboard

React + Flask dashboard comparing Elexon **WINDFOR** day-ahead wind forecasts against
**FUELHH** actual outturn for January 2026.

## Layout

- `backend/` — Flask API, SQLite cache, Elexon ingestion, pytest suite
- `frontend/` — Vite/React SPA, Recharts, TanStack Query
- `docs/` — requirements, build plan, tasks, Elexon sample payloads

## Run locally

### Backend

```bash
cd backend
pip install -r requirements-dev.txt
set FLASK_APP=wsgi:app   # PowerShell: $env:FLASK_APP="wsgi:app"
flask run
```

On first start the backend attempts an Elexon refresh into `backend/data/wind.db`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 (Vite proxies `/api` to Flask).

### Docker Compose

```bash
docker compose up --build
```

## Tests

```bash
cd backend && pytest
cd frontend && npm test
```

## Configuration

See `backend/.env.example` and `frontend/.env.example`. Key settings:

- `DECISION_CUTOFF_LOCAL_TIME` — assumed GB day-ahead gate closure (default `11:00` London)
- `ADMIN_REFRESH_SECRET` — header `X-Admin-Secret` for `POST /api/admin/refresh`
- `CORS_ORIGINS` — Vercel frontend origin(s)

## Deployed apps

- Frontend (Vercel): _add URL after deploy_
- Backend (Render/Heroku): _add URL after deploy_

Set `VITE_API_BASE_URL` on Vercel to the backend URL.

## AI tooling disclosure

This project was built with **Cursor** (AI-assisted editing, test generation, and
documentation). All design choices follow `docs/BUILD_PLAN.md` and were reviewed manually.

## Data attribution

Contains BMRS data © Elexon Limited copyright and database right.
