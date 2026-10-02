from collections import Counter

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Application, Status
from ..schemas import (
    ApplicationCreate,
    ApplicationRead,
    ApplicationUpdate,
    Stats,
    TechCount,
)

router = APIRouter(prefix="/applications", tags=["applications"])


def _get_or_404(db: Session, app_id: int) -> Application:
    obj = db.get(Application, app_id)
    if obj is None:
        raise HTTPException(status_code=404, detail="Postulación no encontrada")
    return obj


@router.post("", response_model=ApplicationRead, status_code=status.HTTP_201_CREATED)
def create_application(payload: ApplicationCreate, db: Session = Depends(get_db)):
    obj = Application(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("", response_model=list[ApplicationRead])
def list_applications(
    status_filter: Status | None = Query(default=None, alias="status"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    stmt = select(Application).order_by(Application.id.desc())
    if status_filter is not None:
        stmt = stmt.where(Application.status == status_filter)
    return db.scalars(stmt.offset(skip).limit(limit)).all()


# Debe ir ANTES de "/{app_id}" para que "stats" no se interprete como un id
@router.get("/stats", response_model=Stats)
def get_stats(top: int = Query(default=10, ge=1, le=50), db: Session = Depends(get_db)):
    apps = db.scalars(select(Application)).all()
    by_status = Counter(a.status.value for a in apps)
    techs = Counter(t for a in apps for t in (a.stack or []))
    return Stats(
        total=len(apps),
        by_status=dict(by_status),
        top_technologies=[TechCount(name=n, count=c) for n, c in techs.most_common(top)],
    )


@router.get("/{app_id}", response_model=ApplicationRead)
def get_application(app_id: int, db: Session = Depends(get_db)):
    return _get_or_404(db, app_id)


@router.patch("/{app_id}", response_model=ApplicationRead)
def update_application(app_id: int, payload: ApplicationUpdate, db: Session = Depends(get_db)):
    obj = _get_or_404(db, app_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/{app_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_application(app_id: int, db: Session = Depends(get_db)):
    db.delete(_get_or_404(db, app_id))
    db.commit()
