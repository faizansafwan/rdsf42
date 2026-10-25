# Deploy backend to Render

Use these settings in the Render **New Web Service** form for repo `faizansafwan/rdsf42`.

## Service settings

| Field | Value |
|--------|--------|
| **Name** | `rdsf42` (or any unique name) |
| **Language** | **Docker** |
| **Branch** | `main` |
| **Root Directory** | `backend` |
| **Region** | Your choice (e.g. Singapore) |
| **Instance type** | Free works for demo; first request after idle may be slow (~50s) |

## Health check (recommended)

After the service is created, open **Settings → Health & Alerts**:

- **Health Check Path:** `/api/health`

## Environment variables

Add these in **Environment** (Production). Generate a strong `ADMIN_REFRESH_SECRET` (e.g. 32+ random characters).

| Key | Value |
|-----|--------|
| `FLASK_ENV` | `production` |
| `DATABASE_PATH` | `/app/data/wind.db` |
| `CORS_ORIGINS` | Your frontend origin, e.g. `https://your-app.vercel.app` (no trailing slash). For local testing only you can add `,http://localhost:5173`. |
| `ADMIN_REFRESH_SECRET` | Long random string (required for `POST /api/admin/refresh`) |
| `ELEXON_API_BASE_URL` | `https://data.elexon.co.uk/bmrs/api/v1` |
| `DECISION_CUTOFF_LOCAL_TIME` | `11:00` |
| `DECISION_DAY_OFFSET` | `-1` |
| `MAPE_ACTUAL_FLOOR_MW` | `50` |
| `SCHEDULER_ENABLED` | `true` |
| `REFRESH_CRON_HOUR` | `6` |
| `REFRESH_CRON_MINUTE` | `0` |

Render injects **`PORT`** automatically; the Dockerfile binds gunicorn to it.

## After deploy

1. Note the public URL, e.g. `https://rdsf42.onrender.com`.
2. Smoke test: `https://rdsf42.onrender.com/api/health` → `{"status":"ok"}`.
3. First load may trigger Elexon refresh (empty DB); wait up to 1–2 minutes, then try  
   `https://rdsf42.onrender.com/api/wind/metrics?start=2026-01-01&end=2026-01-07&resolution=hourly`.
4. On **Vercel**, set `VITE_API_BASE_URL` to the Render URL (no trailing slash), rebuild frontend.
5. Update Render `CORS_ORIGINS` to match the final Vercel URL exactly.

## Free tier notes

- **No persistent disk** — SQLite is recreated when the instance restarts; data is refetched from Elexon on startup when the DB is empty.
- **Spin-down** — inactive free services sleep; first request wakes them (cold start).
- For a stable demo, trigger a manual refresh after deploy:  
  `curl -X POST -H "X-Admin-Secret: YOUR_SECRET" https://YOUR-SERVICE.onrender.com/api/admin/refresh`

## Frontend (Vercel)

- Root directory: `frontend`
- Build command: `npm run build`
- Output directory: `dist`
- Env: `VITE_API_BASE_URL=https://YOUR-SERVICE.onrender.com`
