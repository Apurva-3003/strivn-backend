from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api import auth, checkins, metrics, runs
from app.database import models as _models  # noqa: F401 — register ORM metadata
from app.database.db import Base, engine
from app.services.auth_service import require_secret_key_at_startup


@asynccontextmanager
async def lifespan(app: FastAPI):
    require_secret_key_at_startup()
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="STRIVN API", lifespan=lifespan)

app.include_router(auth.router, prefix="/api")
app.include_router(runs.router, prefix="/api")
app.include_router(checkins.router, prefix="/api")
app.include_router(metrics.router, prefix="/api")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
