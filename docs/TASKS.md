# Build Checklist

Work through in order. Use Cursor's Plan Mode to review each task before switching to
Agent mode to implement it. Run the tests for a phase before starting the next one —
don't let unverified work compound.

## Phase 0 — Scaffolding (~30 min)
- [ ] Create `backend/` and `frontend/` skeletons matching the layout in `AGENTS.md`
- [ ] Add `.gitignore` and `.cursorignore` (exclude `.env`, `node_modules`,
      `__pycache__`, `*.db`, build output)
- [ ] Add `.env.example` with variable names only, no values
- **DoD:** `flask run` and `npm run dev` both start without errors on the empty
  scaffolds.

## Phase 1 — Data pipeline (~2.5–3h)
- [ ] `app/services/elexon_client.py`: fetch `FUELHH/stream` (`fuelType=WIND`) and
      `WINDFOR/stream` with retry/backoff, using the real payload shapes in
      `docs/elexon_sample_responses.md` (bare arrays, WINDFOR filtered by publish time)
      — no Flask or DB imports in this file, it's a pure fetch/parse layer
- [ ] `app/data/models.py` + `app/data/repository.py`: two SQLite tables (`actuals`,
      `forecasts`), upsert keyed as described in `docs/BUILD_PLAN.md` §4–5 — this is
      the only layer that touches SQLite directly
- [ ] `app/services/forecast_matching.py`: implement the D-1 cutoff selection
      (`docs/BUILD_PLAN.md` §3) as pure functions, no I/O, so they're trivially
      unit-testable
- [ ] Validate: 1,488 expected January intervals; log/report any gaps rather than
      silently proceeding
- **DoD:** pytest covers — normal match, multiple same-day forecasts, no forecast
  before cutoff, forecast exactly at the cutoff boundary, missing interval. All green.

## Phase 2 — Metrics (~1h)
- [ ] `app/services/metrics.py`: MAE, RMSE, MAPE, SMAPE, bias; near-zero-actual
      exclusion for MAPE/SMAPE with a documented threshold — pure functions, no I/O
- **DoD:** pytest against hand-computed expected values for a small fixture.

## Phase 3 — Backend API (~2.5–3h)
- [ ] `app/__init__.py`: `create_app()` factory wiring config, extensions, blueprints
- [ ] `app/api/routes.py`: `/api/health`, `/api/wind/compare`, `/api/wind/metrics`,
      `/api/wind/publish-time-distribution`
- [ ] `app/api/admin_routes.py`: `/api/admin/refresh`, gated by a shared secret
- [ ] `app/extensions.py`: CORS allow-list, rate limiting; `app/errors.py`: generic
      JSON error responses with full detail only in server logs
- [ ] Input validation on date params at the route layer, before calling services
- [ ] Stale-cache fallback + `app/jobs/scheduler.py` for scheduled daily refresh
- **DoD:** integration tests pass against a mocked Elexon client — no live network
  calls in CI.

## Phase 4 — Frontend (~3.5–4h)
- [ ] Date range picker + resolution toggle
- [ ] Metric summary cards with plain-English tooltips
- [ ] Forecast-vs-actual chart + error-by-interval chart
- [ ] Loading / error / stale-data states (never a blank screen)
- [ ] Stretch: publish-time histogram
- **DoD:** React Testing Library tests for metric cards and chart rendering on mock
  data; manual check against a running backend.

## Phase 5 — Docker, CI, deploy (~1.5h)
- [ ] `backend/Dockerfile`, root `docker-compose.yml` for local dev
- [ ] GitHub Actions: backend tests + frontend tests + lint on every push
- [ ] Deploy backend to Heroku/Render, frontend to Vercel
- **DoD:** both deployed URLs load, and the frontend successfully calls the live
  backend end-to-end.

## Phase 6 — README, polish, video (~2h)
- [ ] README per the submission brief: file/dir layout, how to run, deployed links,
      explicit AI-tool-usage disclosure
- [ ] Verify every submitted URL in incognito mode
- [ ] Record the video: ≤5 min client pitch, ≤5 min technical walkthrough, ≤10 min
      total

## Phase 7 — QA & bug-fix pass (~3–4h, before Phase 6)
Triggered by a screenshot review that found a blocking rendering bug and several gaps
against the plan. Full detail, root-cause hypotheses, and file-level fixes in
`docs/QA_FIX_PLAN.md` — work through its tiers in order (Tier 0 blocker first, then
Tier 1 required-before-submission items) before doing Phase 6's polish/video pass.
- [ ] Tier 0: forecast line not rendering in the comparison chart
- [ ] Tier 1: data-quality banner, cutoff display, histogram selected-vs-excluded view,
      MAPE exclusion count, date-format risk
- [ ] Tier 2 (if time allows): selected-forecast lag view, accessibility cue, resolution
      toggle verification
