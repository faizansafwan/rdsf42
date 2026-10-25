import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

export default function ForecastVsActualChart({ data }) {
  if (!data?.length) {
    return <p>No comparison data for this range.</p>;
  }

  const chartData = data.map((row) => ({
    time: row.start_time.replace("T", " ").replace("Z", " UTC"),
    actual: row.actual_mw,
    forecast: row.forecast_mw,
  }));

  return (
    <div data-testid="forecast-chart" style={{ width: "100%", height: 320 }}>
      <ResponsiveContainer>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="time" hide={chartData.length > 48} />
          <YAxis unit=" MW" />
          <Tooltip />
          <Legend />
          <Line
            type="monotone"
            dataKey="actual"
            name="Actual (FUELHH)"
            stroke="#0284c7"
            strokeWidth={2}
            dot={false}
          />
          <Line
            type="monotone"
            dataKey="forecast"
            name="D-1 forecast (WINDFOR)"
            stroke="#ea580c"
            strokeWidth={2}
            strokeDasharray="6 4"
            dot={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
