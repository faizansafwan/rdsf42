import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { chartTimeAxisLabel } from "../../utils/formatters";

export default function ErrorBarChart({ data }) {
  if (!data?.length) return null;

  const chartData = data
    .filter((r) => r.error_mw != null)
    .map((row) => ({
      time: row.start_time.replace("T", " ").replace("Z", " UTC"),
      timeLabel: chartTimeAxisLabel(row.start_time, data.length),
      error: row.error_mw,
      label: row.error_mw >= 0 ? "Under-forecast" : "Over-forecast",
    }));

  const pointCount = chartData.length;
  const xHeight = pointCount > 48 ? 72 : 56;

  return (
    <div>
      <ul className="error-legend" aria-label="Error direction legend">
        <li>
          <span className="swatch under" /> Under-forecast (actual higher than forecast)
        </li>
        <li>
          <span className="swatch over" /> Over-forecast (actual lower than forecast)
        </li>
      </ul>
      <div className="chart-container">
        <ResponsiveContainer>
          <BarChart data={chartData} margin={{ bottom: xHeight - 8, left: 4, right: 8 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="timeLabel"
              interval="preserveStartEnd"
              minTickGap={24}
              angle={pointCount > 48 ? -35 : 0}
              textAnchor={pointCount > 48 ? "end" : "middle"}
              height={xHeight}
              tick={{ fontSize: 11 }}
              label={{ value: "Time (UTC)", position: "insideBottom", offset: -4 }}
            />
            <YAxis
              width={72}
              label={{
                value: "Error (MW)",
                angle: -90,
                position: "insideLeft",
                style: { textAnchor: "middle" },
              }}
            />
            <Tooltip
              labelFormatter={(_l, payload) => payload?.[0]?.payload?.time}
              formatter={(v, _n, props) => [
                `${Math.round(v)} MW (${props.payload.label})`,
                "Error",
              ]}
            />
            <Bar dataKey="error" name="Forecast error">
              {chartData.map((entry, i) => (
                <Cell key={i} fill={entry.error >= 0 ? "#0284c7" : "#ea580c"} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
