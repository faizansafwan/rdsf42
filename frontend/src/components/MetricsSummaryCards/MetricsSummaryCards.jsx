import { formatMw, formatPercent, formatSignedMw } from "../../utils/formatters";

const METRICS = [
  {
    key: "mae",
    title: "MAE",
    hint: "Average absolute deviation in MW",
    format: formatMw,
  },
  {
    key: "rmse",
    title: "RMSE",
    hint: "Root mean squared error in MW",
    format: formatMw,
  },
  {
    key: "mape",
    title: "MAPE",
    hint: "Mean absolute % error (low-wind intervals excluded)",
    format: formatPercent,
    caveat: true,
  },
  {
    key: "smape",
    title: "SMAPE",
    hint: "Symmetric MAPE — more stable when output is low",
    format: formatPercent,
  },
  {
    key: "bias",
    title: "Bias",
    hint: "Mean error (actual − forecast); + = under-forecast",
    format: formatSignedMw,
  },
];

export default function MetricsSummaryCards({ metrics, excludedCount, floorMw }) {
  if (!metrics) return null;

  return (
    <div className="card-grid" data-testid="metrics-cards">
      {METRICS.map(({ key, title, hint, format, caveat }) => (
        <article key={key} className="metric-card" title={hint}>
          <h3>{title}</h3>
          <div className="value">{format(metrics[key])}</div>
          <div className="hint">{hint}</div>
          {caveat && excludedCount > 0 && (
            <div className="hint">
              Excluded {excludedCount} intervals with actual &lt; {floorMw} MW
            </div>
          )}
        </article>
      ))}
    </div>
  );
}
