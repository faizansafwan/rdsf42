# AGENTS.md

## Project
A dashboard comparing UK day-ahead wind generation forecasts (WINDFOR) against actual
outturn (FUELHH) for January 2026, for a utility's day-ahead power-buying desk.

- Full requirements (from the product manager): `docs/REQUIREMENTS.md`
- Full design/implementation plan: `docs/BUILD_PLAN.md`
- Ordered build checklist: `docs/TASKS.md`
- Real Elexon API sample payloads + field notes: `docs/elexon_sample_responses.md`

Read all four before writing code. Work through `docs/TASKS.md` in order.

## Stack
- Backend: Python 3.11+, Flask, pandas, pytest
- Frontend: React (Vite), Recharts, TanStack Query
- Storage: SQLite (file-based)
- Deploy: backend → Heroku/Render (Docker); frontend → Vercel (static build)

## Data source
Elexon BMRS Insights API — public, **no API key or registration required**.
- Actuals: `GET https://data.elexon.co.uk/bmrs/api/v1/datasets/FUELHH/stream` (filter `fuelType=WIND`)
- Forecasts: `GET https://data.elexon.co.uk/bmrs/api/v1/datasets/WINDFOR/stream`

Both return a **bare JSON array**, not `{"data": [...]}` — see
`docs/elexon_sample_responses.md` for real example payloads before writing the parser.
`WINDFOR/stream` filters by `publishDateTimeFrom`/`publishDateTimeTo` (publish time, not
delivery time) — fetch using a publish-time window starting **Dec 31, 2025**, since
forecasts for the Jan 1 delivery day were published the day before.

## How to run
- Backend: `cd backend && pip install -r requirements.txt && flask run`
- Frontend: `cd frontend && npm install && npm run dev`
- Tests: `cd backend && pytest` / `cd frontend && npm test`
- Full stack locally: `docker compose up`

## Conventions
- All timestamps stored and processed as UTC; convert to `Europe/London` only at the
  decision-cutoff calculation and at display time.
- Error sign convention: `error = actual − forecast` (positive = under-forecast).
- No secrets in the repo. Env vars documented by name only, in `.env.example`.
- API responses include `{"stale": bool, "last_updated": ISO8601, ...}` so the frontend
  can show a staleness banner when serving cached data.
- `DECISION_CUTOFF_LOCAL_TIME` is a named, configurable constant — never a hardcoded
  assumption buried in logic. See `docs/BUILD_PLAN.md` §1 and §3 for why.

## Directory layout

Backend follows the standard Flask **app-factory + blueprint** pattern with a
service layer (business logic) separated from a repository layer (data access) —
this is what makes `create_app()` testable with a throwaway config and keeps
`forecast_matching.py`/`metrics.py` unit-testable with no Flask or DB involved at
all. Frontend follows the standard Vite/React layering: presentational
`components/`, data-fetching `hooks/` (TanStack Query), and a thin `api/` client —
components never call `fetch` directly.

```
/backend
  /app
    __init__.py            # create_app() factory; registers blueprints & extensions
    config.py               # Config/DevConfig/ProdConfig, reads env vars
    extensions.py            # Flask-Limiter, Flask-Talisman, Flask-CORS init
    errors.py                 # error handlers -> generic JSON, full detail only in logs
    /api
      __init__.py
      routes.py                # blueprint: /api/wind/*, /api/health
      admin_routes.py            # blueprint: /api/admin/refresh (protected)
    /services
      elexon_client.py           # fetch + retry + parse (no Flask/DB imports)
      forecast_matching.py       # D-1 selection logic (pure functions)
      metrics.py                 # MAE/RMSE/MAPE/SMAPE/bias (pure functions)
    /data
      models.py                   # SQLite schema: actuals, forecasts
      repository.py                # upsert/query DAO; only layer that touches SQLite
    /jobs
      scheduler.py                  # APScheduler daily refresh job
  /tests
    conftest.py                      # pytest fixtures: test app, mock Elexon client
    test_forecast_matching.py
    test_metrics.py
    test_api.py
    /fixtures
      sample_elexon_responses.json    # from docs/elexon_sample_responses.md
  wsgi.py                                # entry point: app = create_app()
  requirements.txt
  requirements-dev.txt                    # pytest, responses, pip-audit
  Dockerfile
  .env.example

/frontend
  /public
    favicon.svg
  /src
    main.jsx                           # mounts <App/>, wraps QueryClientProvider
    App.jsx                             # top-level layout
    /api
      windApi.js                         # fetch wrappers for backend endpoints only
    /hooks
      useWindCompare.js                   # TanStack Query hook
      useWindMetrics.js
      usePublishTimeDistribution.js
    /components
      /DateRangePicker
        DateRangePicker.jsx
        DateRangePicker.test.jsx
      /MetricsSummaryCards
      /ForecastVsActualChart
      /ErrorBarChart
      /PublishTimeHistogram
      /DataQualityBanner
      /Layout
    /utils
      formatters.js                       # date/number formatting
    /styles
      index.css
    /test
      setupTests.js
  index.html
  package.json
  vite.config.js
  .env.example

/docs
  REQUIREMENTS.md
  BUILD_PLAN.md
  TASKS.md
  elexon_sample_responses.md
docker-compose.yml
AGENTS.md
README.md
```

Note: this is plain JavaScript, matching the brief's "React" requirement with no
framework assumptions beyond that. TypeScript is a reasonable upgrade for a
client-facing demo if time allows (stricter contracts between `api/` and
`components/`) — say so if you want the structure above switched to `.tsx`/`.ts`
throughout; it's a naming/tooling change, not a different layout.

## Definition of done
Don't mark a task in `docs/TASKS.md` complete until its own acceptance criteria and
tests pass. Don't move to the next phase until the current one is green.
