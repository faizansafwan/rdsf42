import { formatUkDate } from "../../utils/formatters";

export default function DateRangePicker({
  start,
  end,
  resolution,
  onStartChange,
  onEndChange,
  onResolutionChange,
}) {
  return (
    <div className="controls" role="group" aria-label="Date range and resolution">
      <label>
        Start
        <input
          type="date"
          min="2026-01-01"
          max="2026-01-31"
          value={start}
          onChange={(e) => onStartChange(e.target.value)}
          aria-describedby="range-display"
        />
      </label>
      <label>
        End
        <input
          type="date"
          min="2026-01-01"
          max="2026-01-31"
          value={end}
          onChange={(e) => onEndChange(e.target.value)}
          aria-describedby="range-display"
        />
      </label>
      <label>
        Resolution
        <select value={resolution} onChange={(e) => onResolutionChange(e.target.value)}>
          <option value="30min">30 minutes</option>
          <option value="hourly">Hourly (mean of half-hours)</option>
        </select>
      </label>
      <p id="range-display" className="range-display">
        Selected range: <strong>{formatUkDate(start)}</strong> →{" "}
        <strong>{formatUkDate(end)}</strong>
      </p>
    </div>
  );
}
