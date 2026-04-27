import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class MetricsSnapshotBase(BaseModel):
    date: datetime.date
    fitness: int = Field(ge=0, le=100)
    fatigue: int = Field(ge=0, le=100)
    capacity: int = Field(ge=0, le=100)
    sleep_score: int = Field(ge=0, le=100)


class MetricsSnapshotCreate(MetricsSnapshotBase):
    user_id: UUID


class MetricsHistoryResponse(MetricsSnapshotBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: UUID
