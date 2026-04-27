"""Load latest metrics row or a default baseline for TrainingModel updates."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import MetricsHistory


class _DefaultMetrics:
    __slots__ = ()
    fitness = 30
    fatigue = 20
    capacity = 60
    sleep_score = 60


def latest_metrics_readable(db: Session, user_id: UUID) -> MetricsHistory | _DefaultMetrics:
    stmt = (
        select(MetricsHistory)
        .where(MetricsHistory.user_id == user_id)
        .order_by(MetricsHistory.date.desc(), MetricsHistory.id.desc())
        .limit(1)
    )
    row = db.scalars(stmt).first()
    return row if row is not None else _DefaultMetrics()
