const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "";

async function fetchJson(path) {
  const res = await fetch(`${API_BASE}${path}`);
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.error || `Request failed (${res.status})`);
  }
  return res.json();
}

export function getWindCompare(start, end, resolution) {
  const q = new URLSearchParams({ start, end, resolution });
  return fetchJson(`/api/wind/compare?${q}`);
}

export function getWindMetrics(start, end, resolution) {
  const q = new URLSearchParams({ start, end, resolution });
  return fetchJson(`/api/wind/metrics?${q}`);
}

export function getPublishTimeDistribution(date) {
  const q = new URLSearchParams({ date });
  return fetchJson(`/api/wind/publish-time-distribution?${q}`);
}
