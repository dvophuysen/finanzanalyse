// Default: leerer Prefix -> relative Pfade. Funktioniert sowohl im Dev
// (mit Proxy/CORS) als auch hinter HA-Ingress (gleicher Origin).
export const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "";

export async function fetcher<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}/api${path}`, { cache: "no-store" });
  if (!res.ok) throw new Error(`API ${path} -> ${res.status}`);
  return (await res.json()) as T;
}

export function api(path: string) {
  return `${API_BASE}/api${path}`;
}

export function fmtEUR(n: number | string) {
  const v = typeof n === "string" ? parseFloat(n) : n;
  return new Intl.NumberFormat("de-DE", {
    style: "currency",
    currency: "EUR",
  }).format(v);
}
