from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.database.models import MetricsHistory, User
from app.schemas.metrics_schema import MetricsHistoryResponse
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("/latest", response_model=MetricsHistoryResponse)
def get_latest_metrics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MetricsHistory:
    stmt = (
        select(MetricsHistory)
        .where(MetricsHistory.user_id == current_user.id)
        .order_by(MetricsHistory.date.desc(), MetricsHistory.id.desc())
        .limit(1)
    )
    row = db.scalars(stmt).first()
    if row is None:
        raise HTTPException(status_code=404, detail="No metrics history for user")
    return row
