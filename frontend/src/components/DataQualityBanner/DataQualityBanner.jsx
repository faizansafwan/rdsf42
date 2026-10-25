export default function DataQualityBanner({ stale, lastUpdated, quality }) {
  if (!stale && !quality?.missing_count) return null;

  return (
    <div className={`banner ${stale ? "warning" : "warning"}`} role="status">
      {stale && (
        <p>
          Showing cached data — live refresh failed. Last updated:{" "}
          {lastUpdated || "unknown"}.
        </p>
      )}
      {quality?.missing_count > 0 && (
        <p>
          Data quality: {quality.missing_count} missing settlement interval(s) in
          range (expected {quality.expected_count}, got {quality.actual_count}).
        </p>
      )}
      {quality?.intervals_with_missing_forecast > 0 && (
        <p>
          {quality.intervals_with_missing_forecast} interval(s) have no D-1 forecast
          before the decision cutoff.
        </p>
      )}
    </div>
  );
}
