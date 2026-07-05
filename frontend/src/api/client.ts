import type { SessionSummary } from "../types/metrics";

// Empty in dev (Vite proxies /api to localhost:8000); set to the backend
// origin when the dashboard is hosted away from the backend (e.g. Netlify).
const BASE = import.meta.env.VITE_API_BASE ?? "";

async function post(path: string) {
  const r = await fetch(BASE + path, { method: "POST" });
  if (!r.ok) throw new Error(`${path} -> ${r.status}`);
  return r.json();
}
async function get<T>(path: string): Promise<T> {
  const r = await fetch(BASE + path);
  if (!r.ok) throw new Error(`${path} -> ${r.status}`);
  return r.json();
}

export const api = {
  start: () => post("/api/session/start"),
  stop: () => post("/api/session/stop"),
  calibrate: () => post("/api/session/calibrate"),
  status: () => get<{ running: boolean; session_id: number | null }>("/api/session/status"),
  sessions: () => get<SessionSummary[]>("/api/sessions"),
  session: (id: number) => get<SessionSummary & { samples: any[] }>(`/api/sessions/${id}`),
};
