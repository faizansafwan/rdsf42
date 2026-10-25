import { formatUkDate } from "../../utils/formatters";

function summarizeByDay(data) {
  const byDay = new Map();
  for (const row of data ?? []) {
    if (!row.publish_time) continue;
    const day = row.start_time.slice(0, 10);
    const entry = byDay.get(day) ?? { day, publishTimes: new Map(), intervals: 0 };
    entry.intervals += 1;
    const pt = row.publish_time;
    entry.publishTimes.set(pt, (entry.publishTimes.get(pt) ?? 0) + 1);
    byDay.set(day, entry);
  }
  return [...byDay.values()]
    .sort((a, b) => a.day.localeCompare(b.day))
    .map((entry) => {
      let topPublish = null;
      let topCount = 0;
      for (const [pt, count] of entry.publishTimes.entries()) {
        if (count > topCount) {
          topPublish = pt;
          topCount = count;
        }
      }
      return {
        day: entry.day,
        intervals: entry.intervals,
        selectedPublishTime: topPublish,
      };
    });
}

export default function SelectedForecastSummary({ data }) {
  const rows = summarizeByDay(data);
  if (!rows.length) {
    return <p>No selected publish times in this range (missing forecasts before cutoff).</p>;
  }

  return (
    <div className="selected-forecast-table-wrap">
      <p className="panel-caption">
        Latest forecast available at gate closure — selected <code>publishTime</code> per
        delivery day (summarized from matched intervals).
      </p>
      <table className="selected-forecast-table">
        <thead>
          <tr>
            <th>Delivery day</th>
            <th>Selected publish time (UTC)</th>
            <th>Intervals matched</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row.day}>
              <td>{formatUkDate(row.day)}</td>
              <td>
                <time dateTime={row.selectedPublishTime}>
                  {row.selectedPublishTime?.replace("T", " ").replace("Z", " UTC")}
                </time>
              </td>
              <td>{row.intervals}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
