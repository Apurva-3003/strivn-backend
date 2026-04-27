import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class RunSubmit(BaseModel):
    """Body for POST /runs (training pipeline)."""

    distance_km: float = Field(ge=0)
    duration_minutes: int = Field(ge=0)
    rpe: int = Field(ge=1, le=10)


class RunBase(BaseModel):
    date: datetime.date
    distance_km: float = Field(ge=0)
    duration_minutes: int = Field(ge=0)
    rpe: int = Field(ge=1, le=10)


class RunCreate(RunBase):
    user_id: UUID


class RunUpdate(BaseModel):
    date: datetime.date | None = None
    distance_km: float | None = Field(default=None, ge=0)
    duration_minutes: int | None = Field(default=None, ge=0)
    rpe: int | None = Field(default=None, ge=1, le=10)


class RunResponse(RunBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: UUID
