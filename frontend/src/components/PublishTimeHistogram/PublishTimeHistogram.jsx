import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

export default function PublishTimeHistogram({ histogram, date }) {
  if (!histogram?.length) {
    return <p>No publish-time data for {date}.</p>;
  }

  const chartData = histogram.map((h) => ({
    hour: `${h.hour_utc}:00 UTC`,
    count: h.count,
  }));

  return (
    <div style={{ width: "100%", height: 240 }}>
      <ResponsiveContainer>
        <BarChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="hour" />
          <YAxis allowDecimals={false} />
          <Tooltip />
          <Bar dataKey="count" fill="#6366f1" name="Forecast publishes" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
