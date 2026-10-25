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
      let modePublish = null;
      let modeCount = 0;
      let latestPublish = null;
      for (const [pt, count] of entry.publishTimes.entries()) {
        if (count > modeCount) {
          modePublish = pt;
          modeCount = count;
        }
        if (!latestPublish || pt > latestPublish) {
          latestPublish = pt;
        }
      }
      return {
        day: entry.day,
        intervals: entry.intervals,
        modePublish,
        modeCount,
        latestPublish,
        uniquePublishTimes: entry.publishTimes.size,
      };
    });
}

export default function SelectedForecastSummary({ data }) {
  const rows = summarizeByDay(data);
  if (!rows.length) {
    return (
      <p>
        No selected publish times in this range. Try 30-minute resolution, or check that
        forecasts exist before the decision cutoff.
      </p>
    );
  }

  return (
    <div className="selected-forecast-table-wrap">
      <p className="panel-caption">
        Dominant selected <code>publishTime</code> per delivery day (from D-1 cutoff
        matching). If all intervals share one publish time, mode and latest coincide.
      </p>
      <table className="selected-forecast-table">
        <thead>
          <tr>
            <th>Delivery day</th>
            <th>Dominant publish time (UTC)</th>
            <th>Intervals with this publish time</th>
            <th>Latest selected (UTC)</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row.day}>
              <td>{formatUkDate(row.day)}</td>
              <td>
                <time dateTime={row.modePublish}>
                  {row.modePublish?.replace("T", " ").replace("Z", " UTC")}
                </time>
                {row.uniquePublishTimes > 1 && (
                  <span className="table-note"> ({row.uniquePublishTimes} distinct publishes)</span>
                )}
              </td>
              <td>
                {row.modeCount} / {row.intervals}
              </td>
              <td>
                {row.latestPublish === row.modePublish ? (
                  "Same as dominant"
                ) : (
                  <time dateTime={row.latestPublish}>
                    {row.latestPublish?.replace("T", " ").replace("Z", " UTC")}
                  </time>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
