from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.database.models import MetricsHistory, Run, User
from app.schemas.metrics_schema import MetricsHistoryResponse
from app.schemas.run_schema import RunResponse, RunSubmit
from app.services.auth_service import get_current_user
from app.services.metrics_access import latest_metrics_readable
from app.services.training_model import TrainingModel

router = APIRouter(prefix="/runs", tags=["runs"])


@router.post("", response_model=MetricsHistoryResponse)
def create_run(
    payload: RunSubmit,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MetricsHistory:
    today = date.today()
    current = latest_metrics_readable(db, current_user.id)
    updated = TrainingModel.update_from_run(
        current,
        payload.distance_km,
        payload.duration_minutes,
        payload.rpe,
    )

    run = Run(
        user_id=current_user.id,
        date=today,
        distance_km=payload.distance_km,
        duration_minutes=payload.duration_minutes,
        rpe=payload.rpe,
    )
    snapshot = MetricsHistory(
        user_id=current_user.id,
        date=today,
        fitness=updated.fitness,
        fatigue=updated.fatigue,
        capacity=updated.capacity,
        sleep_score=updated.sleep_score,
    )
    db.add(run)
    db.add(snapshot)
    db.commit()
    db.refresh(snapshot)
    return snapshot


@router.get("", response_model=list[RunResponse])
def list_runs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Run]:
    stmt = (
        select(Run)
        .where(Run.user_id == current_user.id)
        .order_by(Run.date.desc(), Run.id.desc())
    )
    return list(db.scalars(stmt).all())
