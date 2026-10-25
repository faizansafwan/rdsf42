import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

const ROLE_COLORS = {
  selected: "#16a34a",
  eligible_not_selected: "#94a3b8",
  after_cutoff: "#dc2626",
};

const ROLE_LABELS = {
  selected: "Selected for D-1 decision",
  eligible_not_selected: "Before cutoff, not selected",
  after_cutoff: "After cutoff (excluded)",
};

export default function PublishTimeHistogram({
  distribution,
  histogramDate,
  onDateChange,
  error,
  isLoading,
}) {
  const buckets = distribution?.buckets ?? [];

  if (error) {
    return (
      <div className="banner error" role="alert">
        Could not load publish-time audit: {error.message}
      </div>
    );
  }

  if (isLoading) {
    return <div className="skeleton" style={{ minHeight: 120 }} aria-busy="true" />;
  }

  return (
    <div>
      <div className="controls histogram-controls">
        <label>
          Delivery day for histogram
          <input
            type="date"
            min="2026-01-01"
            max="2026-01-31"
            value={histogramDate}
            onChange={(e) => onDateChange(e.target.value)}
          />
        </label>
      </div>
      <p className="panel-caption">
        {distribution?.x_axis_caption ?? "Distinct publish times observed"} · Gate closure{" "}
        {distribution?.decision_cutoff_local_time} {distribution?.decision_timezone} on
        decision day (D{distribution?.decision_day_offset ?? -1})
      </p>
      {!buckets.length ? (
        <p>No publish-time data for {histogramDate}.</p>
      ) : (
        <div className="chart-container chart-container--histogram">
          <ResponsiveContainer>
            <BarChart data={buckets} margin={{ bottom: 8 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="label" interval={0} angle={-25} textAnchor="end" height={70} />
              <YAxis allowDecimals={false} label={{ value: "Forecast rows", angle: -90, position: "insideLeft" }} />
              <Tooltip
                formatter={(v, name, props) => {
                  const sel = props.payload.selected_intervals ?? 0;
                  const label = ROLE_LABELS[props.payload.role] ?? "Publishes";
                  return [
                    `${v} forecast row(s), ${sel} interval(s) selected for D-1`,
                    label,
                  ];
                }}
              />
              <Legend
                payload={Object.entries(ROLE_LABELS).map(([role, name]) => ({
                  value: name,
                  type: "square",
                  color: ROLE_COLORS[role],
                }))}
              />
              {(() => {
                const marker = buckets.find((b) => b.role === "after_cutoff")?.label;
                if (!marker) return null;
                return (
                  <ReferenceLine
                    x={marker}
                    stroke="#7c2d12"
                    strokeDasharray="4 4"
                    label={{
                      value: `After ${distribution?.decision_cutoff_local_time} cutoff`,
                      position: "top",
                      fill: "#7c2d12",
                    }}
                  />
                );
              })()}
              <Bar dataKey="count" name="Publish events">
                {buckets.map((entry) => (
                  <Cell key={entry.publish_time_utc} fill={ROLE_COLORS[entry.role] ?? "#6366f1"} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}
