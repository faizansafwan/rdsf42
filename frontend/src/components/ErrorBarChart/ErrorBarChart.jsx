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

export default function ErrorBarChart({ data }) {
  if (!data?.length) return null;

  const chartData = data
    .filter((r) => r.error_mw != null)
    .map((row) => ({
      time: row.start_time,
      error: row.error_mw,
      label: row.error_mw >= 0 ? "Under-forecast" : "Over-forecast",
    }));

  return (
    <div style={{ width: "100%", height: 280 }}>
      <ResponsiveContainer>
        <BarChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="time" hide />
          <YAxis unit=" MW" />
          <Tooltip
            formatter={(v, _n, props) => [
              `${Math.round(v)} MW (${props.payload.label})`,
              "Error",
            ]}
          />
          <Bar dataKey="error">
            {chartData.map((entry, i) => (
              <Cell key={i} fill={entry.error >= 0 ? "#0284c7" : "#ea580c"} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
