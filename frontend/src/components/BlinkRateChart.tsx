import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis, ReferenceLine } from "recharts";
import type { ChartPoint } from "../api/useLiveSocket";

export default function BlinkRateChart({ data }: { data: ChartPoint[] }) {
  return (
    <div className="panel chart-wrap">
      <h2>Blink rate · per minute</h2>
      <ResponsiveContainer width="100%" height={200}>
        <LineChart data={data} margin={{ top: 8, right: 12, bottom: 4, left: -18 }}>
          <XAxis dataKey="t" stroke="var(--muted)" fontSize={11} tickFormatter={(s) => `${Math.floor(s / 60)}m`} />
          <YAxis stroke="var(--muted)" fontSize={11} domain={[0, "auto"]} />
          <Tooltip contentStyle={{ background: "var(--panel-2)", border: "1px solid var(--border)", borderRadius: 8, fontFamily: "var(--mono)", fontSize: 12 }} labelFormatter={(s) => `${s}s in`} />
          <ReferenceLine y={12} stroke="var(--medium)" strokeDasharray="4 4" label={{ value: "healthy floor", fill: "var(--muted)", fontSize: 10, position: "insideTopRight" }} />
          <Line type="monotone" dataKey="blinkRate" stroke="var(--iris)" strokeWidth={2} dot={false} isAnimationActive={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
