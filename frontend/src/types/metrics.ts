export type StrainLevel = "low" | "medium" | "high";

export interface LiveMetric {
  avg_ear: number;
  threshold: number;
  cnn_open_prob: number;     // -1 when not evaluated / EAR-only
  blink_count: number;
  blink_rate: number;
  perclos: number;
  proximity: string;
  strain: StrainLevel;
  strain_score: number;
  screen_time_min: number;
  total_screen_time_min: number;
  fps: number;
  face_detected: boolean;
  frame: string | null;      // base64 JPEG
  session_id: number | null;
  ts: number;
}

export interface SessionSummary {
  id: number;
  started_at: string | null;
  ended_at: string | null;
  duration_min: number;
  avg_blink_rate: number;
  avg_perclos: number;
  high_strain_min: number;
  sample_count: number;
}
