import type { SessionSummary } from "../types/metrics";

async function post(path: string) {
  const r = await fetch(path, { method: "POST" });
  if (!r.ok) throw new Error(`${path} -> ${r.status}`);
  return r.json();
}
async function get<T>(path: string): Promise<T> {
  const r = await fetch(path);
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
