import {
  formatMapeWithExclusions,
  formatMw,
  formatPercent,
  formatSignedMw,
} from "../../utils/formatters";

const METRICS = [
  {
    key: "mae",
    title: "MAE",
    hint: "Average absolute deviation in MW",
    formula:
      "MAE = (1/n) × Σ|actual − forecast|. Same units as generation (MW); lower is better.",
    format: (m) => formatMw(m.mae),
  },
  {
    key: "rmse",
    title: "RMSE",
    hint: "Root mean squared error in MW",
    formula:
      "RMSE = √((1/n) × Σ(actual − forecast)²). Penalises large misses more than MAE.",
    format: (m) => formatMw(m.rmse),
  },
  {
    key: "mape",
    title: "MAPE",
    hint: "Mean absolute percentage error",
    formula:
      "MAPE = (100/n) × Σ|actual − forecast|/|actual|. Intervals below the MW floor are excluded so low-wind periods do not dominate.",
    format: (m) =>
      formatMapeWithExclusions(m.mape, m.mape_excluded_count ?? 0, m.mape_floor_mw ?? 50),
  },
  {
    key: "smape",
    title: "SMAPE",
    hint: "Symmetric MAPE — more stable when output is low",
    formula:
      "SMAPE = (200/n) × Σ|actual − forecast|/(|actual| + |forecast|). Uses the same low-wind exclusion as MAPE.",
    format: (m) => formatPercent(m.smape),
  },
  {
    key: "bias",
    title: "Bias",
    hint: "Mean error (actual − forecast); + = under-forecast",
    formula:
      "Bias = (1/n) × Σ(actual − forecast). Positive ⇒ under-forecast (actual wind exceeded the day-ahead forecast).",
    format: (m) => formatSignedMw(m.bias),
  },
];

export default function MetricsSummaryCards({ metrics, resolution }) {
  if (!metrics) return null;

  return (
    <>
      <div className="card-grid" data-testid="metrics-cards">
      {METRICS.map(({ key, title, hint, formula, format }) => (
        <article key={key} className="metric-card">
          <h3>{title}</h3>
          <div className="value">{format(metrics)}</div>
          <div className="hint">{hint}</div>
          <p className="metric-formula" title={formula}>
            {formula}
          </p>
          {key === "mae" && resolution === "hourly" && (
            <div className="hint">Metrics recomputed on hourly means for the selected range.</div>
          )}
        </article>
      ))}
      </div>
    </>
  );
}
