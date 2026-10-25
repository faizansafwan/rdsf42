import { formatRefreshTimestamp } from "../../utils/formatters";

export default function DataQualityBanner({ stale, lastUpdated, quality }) {
  const hasWarnings = stale || (quality?.missing_count ?? 0) > 0;

  return (
    <div className="data-status" role="status">
      <p className="freshness-line">
        Last refreshed: <strong>{formatRefreshTimestamp(lastUpdated)}</strong> (UTC)
        {stale ? (
          <span className="stale-tag"> · Cached data — live refresh failed</span>
        ) : (
          <span className="fresh-tag"> · Live cache</span>
        )}
      </p>
      {hasWarnings && (
        <div className={`banner ${stale ? "warning" : "warning"}`}>
          {stale && (
            <p>
              Showing cached data — live refresh failed. Confirm metrics against the last
              good snapshot before making decisions.
            </p>
          )}
          {quality?.missing_count > 0 && (
            <p>
              Data quality: {quality.missing_count} missing settlement interval(s) in
              range (expected {quality.expected_count}, got {quality.actual_count}).
            </p>
          )}
        </div>
      )}
    </div>
  );
}
