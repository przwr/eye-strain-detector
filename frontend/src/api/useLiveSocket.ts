import { useEffect, useRef, useState } from "react";
import type { LiveMetric } from "../types/metrics";

export interface ChartPoint { t: number; blinkRate: number; perclos: number; }

export function useLiveSocket(active: boolean) {
  const [latest, setLatest] = useState<LiveMetric | null>(null);
  const [history, setHistory] = useState<ChartPoint[]>([]);
  const [connected, setConnected] = useState(false);
  const ws = useRef<WebSocket | null>(null);
  const lastPush = useRef(0);

  useEffect(() => {
    if (!active) return;
    const url = `${location.protocol === "https:" ? "wss" : "ws"}://${location.host}/ws/live`;
    const socket = new WebSocket(url);
    ws.current = socket;
    socket.onopen = () => setConnected(true);
    socket.onclose = () => setConnected(false);
    socket.onmessage = (e) => {
      const m: LiveMetric = JSON.parse(e.data);
      setLatest(m);
      const now = Date.now();
      if (now - lastPush.current >= 1000) {   // one chart point per second
        lastPush.current = now;
        setHistory((h) => [
          ...h.slice(-119),
          { t: Math.round(m.screen_time_min * 60), blinkRate: m.blink_rate, perclos: m.perclos * 100 },
        ]);
      }
    };
    return () => { socket.close(); ws.current = null; };
  }, [active]);

  const reset = () => { setHistory([]); setLatest(null); };
  return { latest, history, connected, reset };
}
