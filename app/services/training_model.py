"""
STRIVN server-side training model: fitness, fatigue, capacity, sleep_score.

Used by API routes to project metrics after runs and daily check-ins.
"""

from __future__ import annotations

from typing import Protocol

from pydantic import BaseModel, ConfigDict


def _clamp(value: int, lo: int = 0, hi: int = 100) -> int:
    return max(lo, min(hi, value))


def _clamp01_10(x: float | int) -> float:
    return max(0.0, min(10.0, float(x)))


class TrainingMetrics(BaseModel):
    """Snapshot of training state (0–100 scales)."""

    model_config = ConfigDict(frozen=True)

    fitness: int
    fatigue: int
    capacity: int
    sleep_score: int


class _MetricsReadable(Protocol):
    fitness: int
    fatigue: int
    capacity: int
    sleep_score: int


class TrainingModel:
    # Run: fatigue ~ distance × RPE; fitness from combined workload
    _RUN_FATIGUE_PER_LOAD = 0.14
    _RUN_FITNESS_DISTANCE_RPE = 0.035
    _RUN_FITNESS_PER_MINUTE = 0.04

    # Check-in: fatigue relief scales with computed sleep_score
    _CHECKIN_FATIGUE_RELIEF = 0.11

    @staticmethod
    def _capacity_from_state(fitness: int, fatigue: int, sleep_score: int) -> int:
        """Correlated capacity: high fatigue or low fitness pulls down; sleep supports."""
        return _clamp(fitness - fatigue + sleep_score // 4)

    @staticmethod
    def update_from_run(
        current_metrics: _MetricsReadable,
        distance_km: float,
        duration_minutes: int,
        rpe: int,
    ) -> TrainingMetrics:
        load = max(0.0, float(distance_km)) * max(1, min(10, int(rpe)))
        d_fatigue = int(round(load * TrainingModel._RUN_FATIGUE_PER_LOAD))
        d_fitness = int(
            round(
                load * TrainingModel._RUN_FITNESS_DISTANCE_RPE
                + max(0, int(duration_minutes)) * TrainingModel._RUN_FITNESS_PER_MINUTE
            )
        )

        fitness = _clamp(int(current_metrics.fitness) + max(0, d_fitness))
        fatigue = _clamp(int(current_metrics.fatigue) + max(0, d_fatigue))
        sleep_score = _clamp(int(current_metrics.sleep_score))
        capacity = TrainingModel._capacity_from_state(fitness, fatigue, sleep_score)

        return TrainingMetrics(
            fitness=fitness,
            fatigue=fatigue,
            capacity=_clamp(capacity),
            sleep_score=sleep_score,
        )

    @staticmethod
    def _sleep_score_from_checkin(
        sleep: float,
        soreness: int,
        energy: int,
        stress: int,
    ) -> int:
        # Hours of sleep: peak at 8h, linear falloff to 0 within ±4h of peak
        sleep_h = max(0.0, float(sleep))
        sleep_component = max(0.0, 25.0 - abs(sleep_h - 8.0) * 6.25)

        s = _clamp01_10(soreness)
        e = _clamp01_10(energy)
        st = _clamp01_10(stress)

        soreness_component = (10.0 - s) * 2.5
        energy_component = e * 2.5
        stress_component = (10.0 - st) * 2.5

        raw = sleep_component + soreness_component + energy_component + stress_component
        return _clamp(int(round(raw)))

    @staticmethod
    def update_from_checkin(
        current_metrics: _MetricsReadable,
        sleep: float,
        soreness: int,
        energy: int,
        stress: int,
    ) -> TrainingMetrics:
        sleep_score = TrainingModel._sleep_score_from_checkin(sleep, soreness, energy, stress)

        fatigue = int(current_metrics.fatigue)
        fatigue -= int(round(sleep_score * TrainingModel._CHECKIN_FATIGUE_RELIEF))
        fatigue = _clamp(fatigue)

        fitness = _clamp(int(current_metrics.fitness))
        capacity = TrainingModel._capacity_from_state(fitness, fatigue, sleep_score)

        return TrainingMetrics(
            fitness=fitness,
            fatigue=fatigue,
            capacity=_clamp(capacity),
            sleep_score=_clamp(sleep_score),
        )
