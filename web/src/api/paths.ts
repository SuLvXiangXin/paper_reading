function normalizeBasePath(value: string): string {
  if (!value || value === "/") return "";
  return value.replace(/\/+$/, "");
}

function detectProxyBasePath(pathname: string): string {
  const match = pathname.match(/^(.*\/proxy\/\d+)(?:\/.*)?$/);
  return normalizeBasePath(match?.[1] ?? "");
}

export function publicBasePath(): string {
  const configured = import.meta.env.VITE_PUBLIC_BASE_PATH;
  if (configured) return normalizeBasePath(configured);
  if (typeof window === "undefined") return "";
  return detectProxyBasePath(window.location.pathname);
}

export function stripPublicBasePath(pathname: string): string {
  const base = publicBasePath();
  if (base && pathname.startsWith(base)) {
    return pathname.slice(base.length) || "/";
  }
  return pathname || "/";
}

export function appUrl(path: string): string {
  const base = publicBasePath();
  const normalized = path.startsWith("/") ? path : `/${path}`;
  if (normalized === "/") return base ? `${base}/` : "/";
  return `${base}${normalized}`;
}

export function apiUrl(path: string): string {
  const configured = import.meta.env.VITE_API_BASE;
  const normalizedApiBase = configured ? configured.replace(/\/+$/, "") : "";
  return `${normalizedApiBase || publicBasePath()}${path}`;
}
