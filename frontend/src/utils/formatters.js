export function formatMw(value) {
  if (value == null || Number.isNaN(value)) return "—";
  return `${Math.round(value).toLocaleString()} MW`;
}

export function formatPercent(value) {
  if (value == null || Number.isNaN(value)) return "—";
  return `${value.toFixed(1)}%`;
}

export function formatSignedMw(value) {
  if (value == null || Number.isNaN(value)) return "—";
  const sign = value > 0 ? "+" : "";
  return `${sign}${Math.round(value).toLocaleString()} MW`;
}
