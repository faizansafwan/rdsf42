import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { chartTimeAxisLabel } from "../../utils/formatters";

function toChartPoint(row, pointCount) {
  const actual =
    row.actual_mw != null && !Number.isNaN(Number(row.actual_mw))
      ? Number(row.actual_mw)
      : null;
  const forecast =
    row.forecast_mw != null && !Number.isNaN(Number(row.forecast_mw))
      ? Number(row.forecast_mw)
      : null;
  const iso = row.start_time;
  return {
    time: iso.replace("T", " ").replace("Z", " UTC"),
    timeLabel: chartTimeAxisLabel(iso, pointCount),
    actual,
    forecast,
  };
}

function ChartTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null;
  const actual = payload.find((p) => p.dataKey === "actual")?.value;
  const forecast = payload.find((p) => p.dataKey === "forecast")?.value;
  return (
    <div className="chart-tooltip">
      <div>{label}</div>
      <div>Actual: {actual != null ? `${Math.round(actual)} MW` : "—"}</div>
      <div>
        Forecast: {forecast != null ? `${Math.round(forecast)} MW` : "— (no D-1 forecast)"}
      </div>
    </div>
  );
}

export default function ForecastVsActualChart({ data }) {
  if (!data?.length) {
    return <p>No comparison data for this range.</p>;
  }

  const pointCount = data.length;
  const chartData = data.map((row) => toChartPoint(row, pointCount));
  const xHeight = pointCount > 48 ? 72 : 56;

  return (
    <div data-testid="forecast-chart">
      <ul className="series-legend" aria-label="Chart series legend">
        <li>
          <span className="series-swatch solid actual" /> Actual (FUELHH) — solid line
        </li>
        <li>
          <span className="series-swatch dashed forecast" /> D-1 forecast (WINDFOR) — dashed
          line; gaps = no matched forecast (hourly WINDFOR rows or post-cutoff)
        </li>
      </ul>
      <div className="chart-container chart-container--tall">
        <ResponsiveContainer>
          <LineChart data={chartData} margin={{ bottom: xHeight - 8, left: 4, right: 8 }}>
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
                value: "Generation (MW)",
                angle: -90,
                position: "insideLeft",
                style: { textAnchor: "middle" },
              }}
            />
            <Tooltip content={<ChartTooltip />} labelFormatter={(_l, payload) => payload?.[0]?.payload?.time} />
            <Line
              type="linear"
              dataKey="actual"
              name="Actual (FUELHH)"
              stroke="#0284c7"
              strokeWidth={2}
              dot={false}
              connectNulls={false}
              isAnimationActive={false}
              legendType="none"
            />
            <Line
              type="linear"
              dataKey="forecast"
              name="D-1 forecast (WINDFOR)"
              stroke="#ea580c"
              strokeWidth={2}
              strokeDasharray="8 5"
              dot={{ r: 3, fill: "#ea580c", strokeWidth: 0 }}
              connectNulls={false}
              isAnimationActive={false}
              legendType="none"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
