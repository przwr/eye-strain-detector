"""Strain scorer -- the eye-strain logic the baseline entirely lacks.

Fuses blinks/min, PERCLOS, continuous screen-time and proximity into a single
0-100 strain score mapped to Low / Medium / High. Rule-based in Phase 1; Phase 2
can swap the weighting for a learned model without changing this interface.
"""
from dataclasses import dataclass, field
from enum import Enum


class StrainLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class StrainResult:
    level: StrainLevel
    score: float
    reasons: list[str] = field(default_factory=list)


class StrainScorer:
    def __init__(
        self,
        low_blink_rate: float = 12.0,
        perclos_warn: float = 0.20,
        break_interval_min: int = 20,
    ) -> None:
        self.low_blink_rate = low_blink_rate
        self.perclos_warn = perclos_warn
        self.break_interval_min = break_interval_min

    def score(
        self,
        *,
        blink_rate: float | None,
        perclos: float | None,
        screen_time_min: float,
        proximity: str,
    ) -> StrainResult:
        score = 0.0
        reasons: list[str] = []

        # 1. Low blink rate -- primary strain signal (normal ~15-20/min).
        # None = insufficient data (e.g. right after returning to the desk).
        if blink_rate is not None and blink_rate < self.low_blink_rate:
            deficit = (self.low_blink_rate - blink_rate) / self.low_blink_rate
            score += 45 * min(1.0, deficit)
            reasons.append(f"low blink rate ({blink_rate:.0f}/min)")

        # 2. PERCLOS -- fatigue / prolonged closure.
        if perclos is not None and perclos > self.perclos_warn:
            over = (perclos - self.perclos_warn) / (1 - self.perclos_warn)
            score += 30 * min(1.0, over)
            reasons.append(f"high eye-closure ({perclos * 100:.0f}%)")

        # 3. Continuous screen time without a break.
        if screen_time_min > self.break_interval_min:
            over = (screen_time_min - self.break_interval_min) / self.break_interval_min
            score += 15 * min(1.0, over)
            reasons.append(f"{screen_time_min:.0f} min without a break")

        # 4. Sitting too close.
        if proximity == "TOO CLOSE":
            score += 10
            reasons.append("sitting too close")

        score = min(100.0, score)
        if score >= 60:
            level = StrainLevel.HIGH
        elif score >= 30:
            level = StrainLevel.MEDIUM
        else:
            level = StrainLevel.LOW
        return StrainResult(level=level, score=score, reasons=reasons)

    def break_due(self, screen_time_min: float, last_break_min: float) -> bool:
        return (screen_time_min - last_break_min) >= self.break_interval_min
