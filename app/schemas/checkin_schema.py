import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CheckinSubmit(BaseModel):
    """Body for POST /checkin (training pipeline)."""

    sleep: float = Field(ge=0)
    soreness: int = Field(ge=0, le=10)
    energy: int = Field(ge=0, le=10)
    stress: int = Field(ge=0, le=10)


class CheckinBase(BaseModel):
    date: datetime.date
    sleep: float = Field(ge=0)
    soreness: int = Field(ge=0)
    energy: int = Field(ge=0)
    stress: int = Field(ge=0)


class CheckinCreate(CheckinBase):
    user_id: UUID


class CheckinUpdate(BaseModel):
    date: datetime.date | None = None
    sleep: float | None = Field(default=None, ge=0)
    soreness: int | None = Field(default=None, ge=0)
    energy: int | None = Field(default=None, ge=0)
    stress: int | None = Field(default=None, ge=0)


class CheckinResponse(CheckinBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: UUID
