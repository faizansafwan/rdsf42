# Elexon BMRS — real sample payloads (for grounding, not guessing)

Base URL: `https://data.elexon.co.uk/bmrs/api/v1` — public, **no API key or
registration required**.

Both endpoints below are the **`/stream`** variants (the ones linked in the original
brief). They return a **bare JSON array** — unlike the non-stream dataset endpoints,
there is **no top-level `{"data": [...]}` wrapper**. Parse accordingly.

## `GET /datasets/FUELHH/stream`

Query params include `fuelType` (array, e.g. `fuelType=WIND`), and either
`publishDateTimeFrom`/`publishDateTimeTo` or `settlementDateFrom`/`settlementDateTo`.

```json
[
  {
    "dataset": "FUELHH",
    "publishTime": "2022-06-25T13:00:00Z",
    "startTime": "2022-06-25T13:00:00Z",
    "settlementDate": "2022-06-25",
    "settlementPeriod": 3,
    "fuelType": "WIND",
    "generation": 4123
  }
]
```

Use `settlementDateFrom=2026-01-01&settlementDateTo=2026-01-31&fuelType=WIND` to pull
January actuals directly.

## `GET /datasets/WINDFOR/stream`

Query params: `publishDateTimeFrom`, `publishDateTimeTo`.

**This filters by publish time, not delivery time.** To get every forecast relevant to
January 2026 deliveries, fetch with a publish-time window starting **2025-12-31**, not
2026-01-01 — the forecasts used for the Jan 1 delivery day were published the day
before.

```json
[
  {
    "dataset": "WINDFOR",
    "publishTime": "2026-07-25T15:52:58.914Z",
    "startTime": "2026-07-25T15:52:58.914Z",
    "generation": 0
  }
]
```

Note: the stream variant carries **no `settlementDate`/`settlementPeriod`** — only
`startTime`. Derive settlement date/period from `startTime` yourself if you need it;
don't expect Elexon to supply it on this endpoint.

## Implications for the fetch/ingestion code

- Both responses are flat arrays → `pd.DataFrame(response.json())` works directly, no
  need to unwrap a `data` key for these two endpoints specifically (other Elexon
  endpoints, like the non-stream `/datasets/WINDFOR`, *do* wrap in `{"data": [...]}` —
  don't assume one shape across all Elexon endpoints).
- Fetch forecasts by **publish-time window** (`2025-12-31T00:00:00Z` to
  `2026-01-31T23:59:59Z`), then do the D-1 cutoff matching in code — don't try to filter
  by delivery date server-side on this endpoint, it isn't a supported parameter here.
- `generation` is in MW on both endpoints; `0` is a meaningful value (e.g. overnight
  lull or a genuinely zero forecast), not a null/missing marker — don't filter it out
  before the MAPE near-zero handling in `metrics.py`.
