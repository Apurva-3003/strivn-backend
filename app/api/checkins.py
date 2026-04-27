from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.database.models import Checkin, MetricsHistory, User
from app.schemas.checkin_schema import CheckinSubmit
from app.schemas.metrics_schema import MetricsHistoryResponse
from app.services.auth_service import get_current_user
from app.services.metrics_access import latest_metrics_readable
from app.services.training_model import TrainingModel

router = APIRouter(prefix="/checkin", tags=["checkins"])


@router.post("", response_model=MetricsHistoryResponse)
def create_checkin(
    payload: CheckinSubmit,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MetricsHistory:
    today = date.today()
    current = latest_metrics_readable(db, current_user.id)
    updated = TrainingModel.update_from_checkin(
        current,
        payload.sleep,
        payload.soreness,
        payload.energy,
        payload.stress,
    )

    checkin = Checkin(
        user_id=current_user.id,
        date=today,
        sleep=payload.sleep,
        soreness=payload.soreness,
        energy=payload.energy,
        stress=payload.stress,
    )
    snapshot = MetricsHistory(
        user_id=current_user.id,
        date=today,
        fitness=updated.fitness,
        fatigue=updated.fatigue,
        capacity=updated.capacity,
        sleep_score=updated.sleep_score,
    )
    db.add(checkin)
    db.add(snapshot)
    db.commit()
    db.refresh(snapshot)
    return snapshot
