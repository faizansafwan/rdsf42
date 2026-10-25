# UK Day-Ahead Wind Forecast Dashboard — Build Plan

Implementation plan for the FUELHH/WINDFOR day-ahead wind forecasting dashboard.
Written for the build itself and for the tech-lead review. See `docs/REQUIREMENTS.md`
for the original brief and `docs/elexon_sample_responses.md` for real API payloads.

## 1. Corrections to the original plan

- **Elexon API needs no key.** FUELHH/WINDFOR are served from the public Insights API
  (`data.elexon.co.uk/bmrs/api/v1`), which requires no registration or key. The
  security risk isn't "don't hardcode the Elexon key" — it's securing *our own* Flask
  API once it's public. An optional key can still be supported via env var for higher
  rate-limit headroom, but it's not a blocker.
- **Don't hardcode the gate-closure time as 11:00/12:00 CET.** That's the EU Single
  Day-Ahead Coupling schedule. GB decoupled from SDAC after Brexit and runs its own
  day-ahead auctions on a different schedule. Make the cutoff a named, documented,
  configurable constant (`DECISION_CUTOFF_LOCAL_TIME`, `Europe/London`) and state the
  assumption explicitly in the pitch rather than presenting a guessed number as fact.
- **Agree with the original review on MAPE.** Add a **bias** (mean error) metric and
  offer **SMAPE** as an alternative; exclude or flag near-zero-actual intervals rather
  than letting MAPE blow up silently.
- **Add:** idempotent/upsert ingestion, stale-cache fallback instead of hard failure,
  explicit UTC storage with timezone conversion only at the display/cutoff boundary,
  and data-completeness validation (1,488 expected half-hour rows for January).
- **WINDFOR/stream filters by publish time, not delivery time** — see
  `docs/elexon_sample_responses.md`. The fetch window for forecasts must start
  2025-12-31, and both `/stream` endpoints return a bare array, not `{"data": [...]}`.

## 2. Architecture overview

```
React SPA (Vercel, static build)
        |  HTTPS, same calls only to our backend
        v
Flask API (Heroku/Render, Dockerized)
   - /api/wind/compare
   - /api/wind/metrics
   - /api/wind/publish-time-distribution
   - /api/health
   - /api/admin/refresh  (protected)
        |
        v
Local cache (SQLite file, 2 tables)  <-- scheduled daily refresh
        |
        v
Elexon BMRS Insights API (FUELHH, WINDFOR) — public, no key
```

The frontend never calls Elexon directly: it only talks to our backend. This keeps
CORS simple, keeps any optional Elexon key server-side only, and lets us
cache/validate/shape the data once instead of in the browser.

## 3. Data pipeline & forecast-selection logic

Fetch window: WINDFOR by **publish time**, `2025-12-31` through `2026-01-31`;
FUELHH by **settlement date**, `2026-01-01` through `2026-01-31`, filtered to
`fuelType=WIND`. Decisions for the Jan 1 delivery day are made on Dec 31, so the
forecast fetch must start one day before the actuals window.

All timestamps are parsed and stored as UTC. Conversion to `Europe/London` happens only
when computing the cutoff and when labeling the UI (this also makes the GMT/BST
question moot in code — `zoneinfo`/`pytz` handles it automatically even though January
itself is all GMT).

```python
DECISION_CUTOFF_LOCAL_TIME = "11:00"   # configurable, documented assumption
DECISION_DAY_OFFSET = -1               # D-1
TZ = "Europe/London"

def select_forecast(start_time_utc, forecasts_for_interval):
    decision_day = localize(start_time_utc, TZ).date() + timedelta(days=DECISION_DAY_OFFSET)
    cutoff_utc = to_utc(decision_day, DECISION_CUTOFF_LOCAL_TIME, TZ)
    candidates = [f for f in forecasts_for_interval if f.publish_time <= cutoff_utc]
    if not candidates:
        return None   # flagged as missing — never silently substitute a later forecast
    return max(candidates, key=lambda f: f.publish_time)
```

Validation: after matching, assert 31 × 48 = 1,488 expected intervals for January; log
and surface (not silently drop) any interval with no actual, no forecast, or a
duplicate `startTime`.

## 4. Backend API design — secure & reliable

**Endpoints**

| Route | Purpose |
|---|---|
| `GET /api/health` | liveness/readiness check for the platform |
| `GET /api/wind/compare?start=&end=&resolution=` | actual vs. matched D-1 forecast series |
| `GET /api/wind/metrics?start=&end=` | MAE/RMSE/MAPE/SMAPE/bias for a range |
| `GET /api/wind/publish-time-distribution?date=` | histogram of forecast publish times (optional) |
| `POST /api/admin/refresh` | manual cache refresh — protected |

**Security**
- CORS allow-list restricted to the exact Vercel frontend origin(s) — never `*`.
- Rate limiting per IP (e.g., `Flask-Limiter`) on all routes, since the backend makes
  outbound calls on the public's behalf.
- Strict input validation on `start`/`end`/`date` query params (whitelist format, bound
  to a sane range) — reject before anything is parsed further.
- Any Elexon key (optional, for rate-limit headroom) and the admin-refresh shared
  secret live only in platform env vars (Heroku config vars / Vercel project settings),
  never in the repo; `.env` stays in `.gitignore`, `.env.example` documents variable
  names only.
- `POST /api/admin/refresh` gated behind a shared-secret header read from env — the
  read-only data endpoints can stay open since there's no PII and no cost to serving
  cached data, but a refresh action can trigger outbound Elexon calls and shouldn't be
  publicly triggerable.
- HTTPS enforced at the platform level (default on Heroku/Vercel); add HSTS and basic
  security headers (`flask-talisman` or manual: `X-Content-Type-Options`,
  `X-Frame-Options`, a simple CSP).
- Generic error responses to the client; full errors/stack traces logged server-side
  only.
- Pin dependencies (`requirements.txt`, `package-lock.json`); run `pip-audit` /
  `npm audit` in CI.

**Reliability**
- Retry wrapper around Elexon calls (e.g., `tenacity`): exponential backoff, capped
  attempts.
- Stale-cache fallback: if a live fetch fails, serve the last good snapshot and return
  `"stale": true` plus `"last_updated"` in the JSON rather than failing the endpoint
  outright.
- Scheduled refresh (daily, e.g. APScheduler) instead of fetching on every request; the
  admin endpoint exists for on-demand refresh during the demo.
- Idempotent ingestion: upsert keyed on `(start_time, publish_time)` so re-running the
  fetch never duplicates rows.

## 5. Storage & caching

SQLite is more than enough for ~1,500 rows; wrap it behind a small repository layer so
swapping to Postgres later is a config change, not a rewrite.

- `actuals(start_time UTC, generation_mw)`
- `forecasts(start_time UTC, publish_time UTC, generation_mw)`

At this volume, computing the D-1 match and the metrics in pandas at request time is
sub-10ms — no need for a separate materialized table, though one can be added later if
the dataset grows.

## 6. Metrics computation

- Define `error = actual − forecast`. Document the sign convention in the UI: positive
  = under-forecast (actual exceeded forecast), negative = over-forecast.
- Compute MAE, RMSE, MAPE, SMAPE, and **bias** (mean error, signed).
- For MAPE/SMAPE, exclude or down-weight intervals where actual generation is below a
  documented threshold (e.g. a fixed MW floor), and show the count of excluded points
  next to the metric rather than hiding the caveat.
- Metrics should be recomputed server-side for whatever date range the UI requests
  (vectorized pandas ops), not just for the full month.

## 7. Frontend / UX design plan

**Stack:** React, a lightweight chart library (Recharts or Chart.js), TanStack Query
for data fetching (gives caching, retries, and loading/error states without
hand-rolling them).

**Components**
- Date-range picker (default: all of January 2026) + a 30-min/hourly resolution toggle.
- Metric summary cards (MAE, RMSE, MAPE, SMAPE, Bias), each with a plain-English
  tooltip (e.g. "MAE — average deviation in MW") and the MAPE card flagged with a
  caveat note.
- Forecast-vs-actual time series chart: two lines, shaded error band, hover tooltip
  with exact MW and timestamp.
- Error-by-interval bar chart, colour-coded over-/under-forecast (not colour-only —
  label it too, for accessibility).
- Optional stretch: publish-time histogram per delivery date, to visually confirm
  "day-ahead" selection is working as intended.
- Data-quality banner: shows missing-interval count and a stale-cache warning when the
  API reports `stale: true`.
- Footer: BMRS data attribution ("Contains BMRS data © Elexon Limited copyright and
  database right"), link to source, and the required note on AI-tool usage.

**Resilience & responsiveness**
- Skeleton loaders while fetching; a clear error banner with a retry action if the
  backend is unreachable — never a blank screen.
- Responsive grid/flex layout; charts resize to container width; cards stack
  vertically on narrow screens.
- Colour-blind-safe palette for the two series, with redundant text/line-style cues.

## 8. Testing strategy

- **Backend (pytest):** forecast-selection logic (normal case, multiple same-day
  forecasts, no forecast before cutoff, forecast exactly at the cutoff boundary,
  missing interval); metrics functions against known inputs/outputs; API integration
  tests against a mocked Elexon client (e.g. `responses`) so CI doesn't depend on
  Elexon's uptime.
- **Frontend (React Testing Library):** metric cards render given mock data; chart
  renders given mock data; date-range picker updates the query.
- **CI:** GitHub Actions running backend tests, frontend tests, and lint on every push
  — this is also good evidence of development practice for the tech-lead review video.

## 9. Docker & deployment

- `backend/Dockerfile`: slim Python base, used for the Heroku/Render deploy.
- Frontend ships as a static Vercel build; it doesn't need its own Docker image in
  production, but a `frontend/Dockerfile` + root `docker-compose.yml` is still worth
  including for local dev parity — note in the README that production uses Vercel +
  Heroku rather than compose, so reviewers aren't confused about which is "the"
  deployment.
- `/api/health` doubles as the platform health check.
- All config (Elexon key if used, admin-refresh secret, allowed CORS origin) via env
  vars, documented in `.env.example`.

## 10. README & submission checklist

- File/directory layout, how to run locally (with and without Docker), and the live
  Vercel/Heroku links — as required by the brief.
- Explicit statement of which AI tools were used and how.
- Before submitting: open every submitted URL in incognito mode to confirm access;
  confirm the repo name is an anonymous random string; keep the video ≤10 minutes
  total, ≤5 minutes per part.

## 11. Suggested 16-hour budget

| Phase | Hours |
|---|---|
| Project setup + data pipeline (fetch, match, validate) | 3.0 |
| Metrics implementation | 1.0 |
| Backend API: endpoints, caching, security, reliability | 3.0 |
| Frontend core (charts, cards, date picker, states) | 4.0 |
| Tests (backend + frontend) | 1.5 |
| Docker + CI + deploy (Vercel/Heroku) | 1.5 |
| README, polish, video recording | 2.0 |

Treat the publish-time histogram and SMAPE toggle as stretch items to cut first if
time runs short.

## 12. Edge cases & risks

| Risk | Why it matters | Mitigation |
|---|---|---|
| No forecast published before cutoff for an interval | Silent gaps would misreport accuracy | Flag as missing in both data and UI; never backfill with a later forecast |
| Elexon API down or slow | Demo/backend fails live | Stale-cache fallback with `stale: true` flag; retries with backoff |
| Duplicate or out-of-order API rows | Double-counted or shifted metrics | Upsert by `(start_time, publish_time)`; validate row counts |
| MAPE near-zero actuals | Metric spikes to absurd values | Exclude/flag below a documented floor; show SMAPE and bias alongside |
| Hardcoded, unverified gate-closure time | Misrepresents the "day-ahead" logic to the client | Configurable constant, documented assumption, stated in the pitch |
| Open admin/refresh endpoint | Lets anyone trigger outbound Elexon calls via our server | Shared-secret header, rate limiting |
| Timezone handling around cutoff | Off-by-one-interval matching errors | Store UTC internally; convert only at cutoff/display boundary using `zoneinfo` |
| WINDFOR/stream filters by publish time, not delivery time | Fetching by the wrong date range silently misses forecasts | Fetch by `publishDateTimeFrom=2025-12-31`; see `docs/elexon_sample_responses.md` |
