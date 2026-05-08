// Relative URLs, damit das in HA Ingress via injiziertem <base href> funktioniert.
export const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "";

function buildUrl(path: string): string {
  const rel = path.startsWith("/") ? path.slice(1) : path;
  return API_BASE ? `${API_BASE}/api/${rel}` : `api/${rel}`;
}

export async function fetcher<T>(path: string): Promise<T> {
  const res = await fetch(buildUrl(path), { cache: "no-store" });
  if (!res.ok) throw new Error(`API ${path} -> ${res.status}`);
  return (await res.json()) as T;
}

export function api(path: string) {
  return buildUrl(path);
}

export function fmtEUR(n: number | string) {
  const v = typeof n === "string" ? parseFloat(n) : n;
  return new Intl.NumberFormat("de-DE", {
    style: "currency",
    currency: "EUR",
  }).format(v);
}
