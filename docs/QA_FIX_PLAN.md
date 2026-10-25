# QA & Bug-Fix Plan

Generated from a screenshot review of the running app, cross-checked against two
external AI reviews (Gemini, DeepSeek) and `docs/BUILD_PLAN.md`. See the chat message
that introduced this file for the full verification table of which external claims were
accepted, rejected, or needed nuance.

Work top to bottom. Don't start Tier 2 until Tier 0/1 are verified fixed — a broken
comparison chart makes everything built on top of it unreviewable.

---

## Tier 0 — Blocker (fix first, nothing else matters until this works)

### T0.1 — Forecast line missing from "Forecast vs actual" chart
- **Root cause hypotheses (check in this order):**
  1. `app/components/ForecastVsActualChart` isn't rendering two `<Line>` elements —
     only one `dataKey` (likely `actual`) is mapped; the `forecast` series has no
     corresponding `<Line>`.
  2. The forecast `<Line>` exists but its `dataKey` doesn't match the key actually
     present in the chart data array (e.g. hook flattens `{actual, forecast}` under a
     different key name than the component expects).
  3. `GET /api/wind/compare` isn't merging both series on `startTime` at all — check
     the raw JSON response directly (`curl` or browser devtools network tab) before
     touching the frontend.
- **Why we're confident it's a bug, not a subtle rendering overlap:** bias is −1,840 MW
  against an MAE of 2,107 MW — that's ~87% systematic error, not noise. A correctly
  rendered chart would show a clear, consistent vertical gap between the two lines
  across nearly the whole month. Seeing one line means the series isn't being drawn,
  full stop.
- **Fix:** confirm the API payload has both series merged on `startTime`; fix the
  hook/component's `dataKey` mapping; add two explicit `<Line dataKey="actual">` /
  `<Line dataKey="forecast">` with distinct `strokeDasharray` (solid vs. dashed) so a
  future overlap is visually distinguishable even when values are close.
- **Also decide and implement:** when `forecast` is `null` for a missing interval
  (never backfilled, per `BUILD_PLAN.md` §3), the line must show a visible **gap**,
  not interpolate across it — this is the honest way to represent "no forecast existed
  before cutoff," and it's directly auditable by the client.
- **Verify:** load the chart with the full January range; confirm both lines are
  visible and the orange line sits above the blue line on most days (consistent with
  the negative bias); toggle a series off/on in the legend to confirm they're
  independently rendered.
- **Est:** 30–60 min.

---

## Tier 1 — Required before submission (plan already specifies these; they're missing or wrong)

### T1.1 — Data-quality / stale-cache banner not visible
- **Check:** is `/api/wind/compare` actually returning `{"stale": bool,
  "last_updated": ..., "missing_intervals": n, "data": [...]}` per `AGENTS.md`
  conventions? If yes, is `DataQualityBanner` mounted and reading that field? If the
  cache happens to be fresh with zero gaps, the banner may be correctly hidden — but
  that can't be confirmed from a screenshot.
- **Fix:** add a small always-visible "Last refreshed: <timestamp>" line even when
  not stale, so freshness is never ambiguous; force a `stale: true` state in dev
  (temporarily block the Elexon call) to confirm the banner itself renders correctly.
- **Est:** 30 min.

### T1.2 — Gate-closure cutoff value isn't shown anywhere
- The subtitle says "configurable gate closure" but never states what it's
  configured *to*. Show it explicitly, e.g. "Cutoff: 11:00 Europe/London" next to the
  subtitle or date pickers — this is the one fact the client's core requirement #1
  ("clearly understand the latest forecast available when they need to decide")
  actually hinges on.
- **Fix location:** expose `DECISION_CUTOFF_LOCAL_TIME` via the `/api/wind/metrics` or
  `/compare` response metadata; render it in the header component.
- **Est:** 20 min.

### T1.3 — Publish-time histogram doesn't demonstrate D-1 selection
- Its stated purpose (`BUILD_PLAN.md` §7) is to *verify* the cutoff logic, not just
  show that forecasts exist. Currently every bar is the same colour with no cutoff
  marker.
- **Fix:** add a vertical reference line at the cutoff time; colour/highlight the one
  bar corresponding to the actually-selected publish time differently from the rest
  (selected vs. correctly-excluded).
- **Also fix:** the chart is hardcoded to `2026-01-01` and ignores the Start/End
  pickers above it. Either add its own day selector or drive it from the selected
  range's first day, and say which in the subtitle.
- **Also fix (cosmetic but real):** bucket labels (`2:00, 4:00, 7:00, 9:00, 11:00,
  15:00, 18:00, 22:00`) are unevenly spaced — use a consistent interval or explicitly
  label the axis as "distinct publish times observed," not a fixed scale.
- **Est:** 1–1.5h.

### T1.4 — MAPE card hides the exclusion count
- Plan requirement (`BUILD_PLAN.md` §6): show the count of excluded points, not just
  that exclusion happened.
- **Fix:** change subtext to something like "MAPE — 21.9% (37 low-wind intervals
  excluded, below 100 MW)." The backend `metrics.py` already computes the excluded
  set; just return the count and threshold alongside the metric value.
- **Est:** 20 min.

### T1.5 — Date picker format is locale-dependent, risky for a UK demo
- `01/01/2026 → 01/31/2026` reads as US `MM/DD/YYYY`; `01/31` isn't valid as a UK
  date at all. If this is a native `<input type="date">`, the display format follows
  whichever machine renders it — don't let a client demo depend on that.
- **Fix:** either force a custom-rendered format (`DD/MM/YYYY` or unambiguous
  `31 Jan 2026`) in the date-picker component, or explicitly verify and screen-record
  on a machine set to `en-GB` before the pitch video.
- **Est:** 20–40 min.

---

## Tier 2 — Strengthens the audit story (not blockers, but directly serve the client's actual ask)

### T2.1 — Add a "selected forecast" lag view
- The client's requirement #1 is specifically "what was the latest forecast I had
  at the decision cutoff?" Right now that's only inferable from the histogram. Add a
  table or hover tooltip showing the **selected `publishTime`** per interval (or
  summarized per day) — this makes the core requirement directly auditable rather
  than inferred.
- **Est:** 45–60 min.

### T2.2 — Error chart needs a non-colour-coded cue
- Plan explicitly requires this (`BUILD_PLAN.md` §7: "not colour-only"). Add a
  legend with text ("Under-forecast" / "Over-forecast") and/or a hatch pattern on one
  series, not just reliance on the chart's text subtitle.
- **Est:** 20–30 min.

### T2.3 — Verify hourly resolution toggle aggregates correctly
- Confirm switching "30 minutes" → "hourly" actually re-aggregates (mean of the two
  half-hours, most likely) both the chart and the recomputed metrics — not just a
  cosmetic axis change. Document the aggregation method in a UI tooltip either way.
- **Est:** 20 min to verify, more if it's actually broken.

---

## Tier 3 — Polish (do only if time remains)

- [x] Add axis titles: Y-axis "Generation (MW)" (fix the wrapping "MW" text), X-axis
      "Time (UTC)" on both charts.
- [x] Hover tooltip on metric cards showing the formula, not just the static subtext.
- [x] Use `−` (U+2212) consistently for negative values instead of ASCII `-`.
- [x] Confirm legend swatches visually match each line's actual style (solid vs.
      dashed) once T0.1 introduces distinct dash patterns.
- [x] **Deliberate, not default:** decide whether "Built with AI-assisted development
      (Cursor)" belongs on the client-facing pitch view, or only in the tech-lead
      walkthrough and README — currently it's on by default on every view.

---

## Tier 4 — Pre-submission checklist (already defined in `docs/TASKS.md` Phase 6 — just confirm, nothing new here)

- [ ] Backend endpoints verified live via `curl`
- [ ] Stale-cache fallback demonstrated on camera
- [ ] 1,488 expected intervals validated; gaps logged and surfaced
- [ ] CI green
- [ ] `docker compose up` works locally
- [ ] README complete (layout, run instructions, deployed links, AI-tool disclosure)
- [ ] All submitted URLs verified in incognito
- [ ] Repo name is an anonymous random string
- [ ] Video ≤10 min total, ≤5 min per part

---

## Estimated additional effort

Tier 0 + Tier 1 ≈ 3–4 hours. Tier 2 ≈ 1.5–2 hours. Tier 3 ≈ 1 hour if time allows.
Tier 0 and 1 are not optional — they're the difference between "looks right" and
"obviously correct" under a tech-lead's or UK client's scrutiny.
