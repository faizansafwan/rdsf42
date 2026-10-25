const MINUS = "\u2212";

export function formatMw(value) {
  if (value == null || Number.isNaN(value)) return "—";
  return `${Math.round(value).toLocaleString("en-GB")} MW`;
}

export function formatPercent(value) {
  if (value == null || Number.isNaN(value)) return "—";
  return `${value.toFixed(1)}%`;
}

export function formatMapeWithExclusions(value, excludedCount, floorMw) {
  if (value == null || Number.isNaN(value)) return "—";
  const base = `${value.toFixed(1)}%`;
  if (!excludedCount) return base;
  return `${base} (${excludedCount} low-wind intervals excluded, below ${floorMw} MW)`;
}

export function formatSignedMw(value) {
  if (value == null || Number.isNaN(value)) return "—";
  const abs = Math.round(Math.abs(value)).toLocaleString("en-GB");
  if (value > 0) return `+${abs} MW`;
  if (value < 0) return `${MINUS}${abs} MW`;
  return `0 MW`;
}

/** ISO date (YYYY-MM-DD) → unambiguous UK display, e.g. 31 Jan 2026 */
export function formatUkDate(isoDate) {
  if (!isoDate) return "—";
  const [y, m, d] = isoDate.split("-").map(Number);
  const dt = new Date(Date.UTC(y, m - 1, d));
  return dt.toLocaleDateString("en-GB", {
    day: "numeric",
    month: "short",
    year: "numeric",
    timeZone: "UTC",
  });
}

/** X-axis tick label for charts (UTC). Compacts automatically for long series. */
export function chartTimeAxisLabel(isoTime, pointCount) {
  const raw = String(isoTime).replace("T", " ").replace("Z", " UTC");
  const d = new Date(String(isoTime).replace("Z", "+00:00"));
  if (Number.isNaN(d.getTime())) return raw;

  if (pointCount > 120) {
    return d.toLocaleDateString("en-GB", {
      day: "numeric",
      month: "short",
      timeZone: "UTC",
    });
  }
  if (pointCount > 48) {
    return d.toLocaleString("en-GB", {
      day: "numeric",
      month: "short",
      hour: "2-digit",
      timeZone: "UTC",
      hour12: false,
    });
  }
  return d.toLocaleString("en-GB", {
    day: "numeric",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
    timeZone: "UTC",
    hour12: false,
  });
}

export function formatRefreshTimestamp(iso) {
  if (!iso) return "unknown";
  const dt = new Date(iso);
  return dt.toLocaleString("en-GB", {
    dateStyle: "medium",
    timeStyle: "short",
    timeZone: "UTC",
  });
}
