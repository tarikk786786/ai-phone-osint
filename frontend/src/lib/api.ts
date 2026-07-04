const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

interface ApiOptions {
  method?: string;
  body?: unknown;
  token?: string;
  apiKey?: string;
}

async function fetchApi<T>(path: string, options: ApiOptions = {}): Promise<T> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };

  if (options.token) {
    headers["Authorization"] = `Bearer ${options.token}`;
  }

  if (options.apiKey) {
    headers["X-API-Key"] = options.apiKey;
  }

  const response = await fetch(`${API_BASE}${path}`, {
    method: options.method || "GET",
    headers,
    body: options.body ? JSON.stringify(options.body) : undefined,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(error.detail || `API error: ${response.status}`);
  }

  return response.json();
}

// ── Auth ───────────────────────────────────────────────

export async function login(username: string, password: string) {
  return fetchApi<{
    access_token: string;
    refresh_token: string;
    user: Record<string, unknown>;
  }>("/auth/login", {
    method: "POST",
    body: { username, password },
  });
}

export async function register(email: string, username: string, password: string) {
  return fetchApi<{
    access_token: string;
    refresh_token: string;
    user: Record<string, unknown>;
  }>("/auth/register", {
    method: "POST",
    body: { email, username, password },
  });
}

// ── Phone Lookup ───────────────────────────────────────

export async function validatePhone(phone: string, country?: string, token?: string) {
  const params = new URLSearchParams({ phone });
  if (country) params.set("country", country);
  return fetchApi<{ success: boolean; data: Record<string, unknown> }>(
    `/lookup/validate?${params}`,
    { token }
  );
}

export async function fullLookup(
  phone: string,
  options?: {
    country?: string;
    includeOsint?: boolean;
    includeGeolocation?: boolean;
    includeAi?: boolean;
    aiProvider?: string;
    token?: string;
  }
) {
  const params = new URLSearchParams({ phone });
  if (options?.country) params.set("country", options.country);
  if (options?.includeOsint !== undefined) params.set("include_osint", String(options.includeOsint));
  if (options?.includeGeolocation !== undefined)
    params.set("include_geolocation", String(options.includeGeolocation));
  if (options?.includeAi !== undefined) params.set("include_ai", String(options.includeAi));
  if (options?.aiProvider) params.set("ai_provider", options.aiProvider);

  return fetchApi<{
    success: boolean;
    data: Record<string, unknown>;
    osint?: Record<string, unknown>;
    geolocation?: Record<string, unknown>;
    ai_report?: Record<string, unknown>;
    lookup_id?: string;
  }>(`/lookup/lookup?${params}`, { token: options?.token });
}

// ── History ────────────────────────────────────────────

export async function getHistory(limit = 20, offset = 0, token: string) {
  return fetchApi<{ success: boolean; data: Record<string, unknown>[] }>(
    `/lookup/history?limit=${limit}&offset=${offset}`,
    { token }
  );
}
