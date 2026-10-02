from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from . import models  # noqa: F401  (registra los modelos en Base.metadata)
from .database import Base, engine, get_db
from .routers import applications


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Simple para la Fase 1. Más adelante se reemplaza por migraciones con Alembic.
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="JobTracker API",
    description="Registro de postulaciones laborales y tecnologías más pedidas.",
    version="0.1.0",
    lifespan=lifespan,
)
app.include_router(applications.router)


@app.get("/health", tags=["ops"])
def health(db: Session = Depends(get_db)):
    """Usado por Docker, Kubernetes y el pipeline para saber si la app está viva."""
    try:
        db.execute(text("SELECT 1"))
    except Exception as exc:
        raise HTTPException(status_code=503, detail="database unavailable") from exc
    return {"status": "ok"}
