import { useEffect, useState } from "react";
import { api } from "../api/client";
import type { SessionSummary } from "../types/metrics";

const STRAIN_BG: Record<string, string> = {
  ok: "rgba(63,182,139,.15)", warn: "rgba(230,180,80,.15)",
};

export default function History() {
  const [sessions, setSessions] = useState<SessionSummary[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.sessions().then(setSessions).finally(() => setLoading(false));
  }, []);

  const fmtDate = (s: string | null) =>
    s ? new Date(s).toLocaleString(undefined, { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" }) : "—";

  return (
    <div className="panel">
      <h2>Session history</h2>
      {loading ? (
        <div className="empty">Loading…</div>
      ) : sessions.length === 0 ? (
        <div className="empty">No sessions yet. Start monitoring on the dashboard to record one.</div>
      ) : (
        <>
          <div className="session-row head">
            <div>Started</div><div>Duration</div><div>Avg blink rate</div><div>Avg PERCLOS</div><div>High strain</div>
          </div>
          {sessions.map((s) => {
            const healthy = s.avg_blink_rate >= 12;
            return (
              <div className="session-row" key={s.id}>
                <div className="mono">{fmtDate(s.started_at)}</div>
                <div className="mono">{s.duration_min} min</div>
                <div>
                  <span className="tag" style={{ background: healthy ? STRAIN_BG.ok : STRAIN_BG.warn, color: healthy ? "var(--low)" : "var(--medium)" }}>
                    {s.avg_blink_rate}/min
                  </span>
                </div>
                <div className="mono">{(s.avg_perclos * 100).toFixed(0)}%</div>
                <div className="mono">{s.high_strain_min} min</div>
              </div>
            );
          })}
        </>
      )}
    </div>
  );
}
