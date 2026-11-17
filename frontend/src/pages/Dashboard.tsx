import { useEffect, useState } from "react";
import { api } from "../api/client";
import { useLiveSocket } from "../api/useLiveSocket";
import IrisGauge from "../components/IrisGauge";
import LiveFeed from "../components/LiveFeed";
import Controls from "../components/Controls";
import BreakAlert from "../components/BreakAlert";
import BlinkRateChart from "../components/BlinkRateChart";

export default function Dashboard() {
  const [running, setRunning] = useState(false);
  const [glasses, setGlasses] = useState(false);
  const { latest, history, connected, reset } = useLiveSocket(running);

  useEffect(() => {
    api.status().then((s) => { setRunning(s.running); setGlasses(s.glasses); }).catch(() => {});
  }, []);

  const start = async () => { await api.start(); reset(); setRunning(true); };
  const stop = async () => { await api.stop(); setRunning(false); };
  const calibrate = () => { api.calibrate().catch(() => {}); };
  const toggleGlasses = () => {
    const next = !glasses;
    setGlasses(next);
    api.glasses(next).catch(() => setGlasses(!next));
  };

  const score = latest?.strain_score ?? 0;
  const level = latest?.strain ?? "low";
  const fmt = (n: number | undefined, d = 0) => (n === undefined ? "—" : n.toFixed(d));

  return (
    <div>
      {level === "high" && <BreakAlert />}
      <div className="grid">
        <div>
          <LiveFeed frame={latest?.frame ?? null} running={running} />
          <BlinkRateChart data={history} />
        </div>

        <div>
          <div className="panel">
            <h2>Strain index</h2>
            <IrisGauge score={score} level={level} />
            <div className="stats">
              <div className="stat">
                <div className="k">Blink rate</div>
                <div className="v">{fmt(latest?.blink_rate)} <span className="u">/min</span></div>
              </div>
              <div className="stat">
                <div className="k">PERCLOS</div>
                <div className="v">{fmt((latest?.perclos ?? 0) * 100)}<span className="u">%</span></div>
              </div>
              <div className="stat">
                <div className="k">Blinks</div>
                <div className="v">{latest?.blink_count ?? "—"}</div>
              </div>
              <div className="stat">
                <div className="k">Since break</div>
                <div className="v">{fmt(latest?.screen_time_min, 1)}<span className="u">min</span></div>
              </div>
              <div className="stat">
                <div className="k">Total screen</div>
                <div className="v">{fmt(latest?.total_screen_time_min, 1)}<span className="u">min</span></div>
              </div>
            </div>
            <Controls running={running} glasses={glasses} onStart={start} onStop={stop} onCalibrate={calibrate} onToggleGlasses={toggleGlasses} />
            {running && !connected && (
              <p style={{ color: "var(--muted)", fontSize: 12, marginTop: 12, fontFamily: "var(--mono)" }}>
                connecting to live feed…
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
