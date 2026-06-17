import type { StrainLevel } from "../types/metrics";

const COLORS: Record<StrainLevel, string> = {
  low: "var(--low)", medium: "var(--medium)", high: "var(--high)",
};

interface Props { score: number; level: StrainLevel; reasons?: string[]; }

/** Concentric "iris" rings; the outer ring arc fills with the strain score. */
export default function IrisGauge({ score, level, reasons = [] }: Props) {
  const size = 200, stroke = 12, r = (size - stroke) / 2 - 6;
  const c = 2 * Math.PI * r;
  const pct = Math.min(100, Math.max(0, score)) / 100;
  const color = COLORS[level];

  return (
    <div className="iris-wrap">
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="var(--border)" strokeWidth={stroke} />
        <circle
          cx={size / 2} cy={size / 2} r={r} fill="none" stroke={color} strokeWidth={stroke}
          strokeLinecap="round" strokeDasharray={c} strokeDashoffset={c * (1 - pct)}
          transform={`rotate(-90 ${size / 2} ${size / 2})`}
          style={{ transition: "stroke-dashoffset .5s ease, stroke .5s ease" }}
        />
        {/* iris inner rings */}
        <circle cx={size / 2} cy={size / 2} r={r - 26} fill="none" stroke={color} strokeWidth={1} opacity={0.25} />
        <circle cx={size / 2} cy={size / 2} r={r - 38} fill="none" stroke={color} strokeWidth={1} opacity={0.18} />
        <circle cx={size / 2} cy={size / 2} r={14} fill={color} opacity={0.9} />
      </svg>
      <div className="iris-level" style={{ color }}>{level}</div>
      <div className="iris-score">strain index {Math.round(score)}/100</div>
      {reasons.length > 0 && (
        <div className="iris-reasons">
          {reasons.map((r2, i) => <div className="reason" key={i}>{r2}</div>)}
        </div>
      )}
    </div>
  );
}
