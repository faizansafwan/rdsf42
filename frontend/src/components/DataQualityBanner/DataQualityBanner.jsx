export default function DataQualityBanner({ stale, quality }) {
  const hasWarnings = stale || (quality?.missing_count ?? 0) > 0;
  if (!hasWarnings) return null;

  return (
    <div className="data-status" role="status">
      <div className="banner warning">
        {stale && (
          <p>
            Showing cached data — live refresh failed. Confirm metrics against the last
            good snapshot before making decisions.
          </p>
        )}
        {quality?.missing_count > 0 && (
          <p>
            Missing actuals: {quality.missing_count} settlement interval(s) in range
            (expected {quality.expected_count}, got {quality.actual_count}).
          </p>
        )}
      </div>
    </div>
  );
}
