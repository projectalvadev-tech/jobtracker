from datetime import date

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .models import Status


def _normalize_stack(values: list[str]) -> list[str]:
    """Minúsculas, sin espacios y sin duplicados (conserva el orden)."""
    seen: dict[str, None] = {}
    for v in values:
        clean = v.strip().lower()
        if clean:
            seen.setdefault(clean, None)
    return list(seen)


class ApplicationBase(BaseModel):
    company: str = Field(min_length=1, max_length=120)
    position: str = Field(min_length=1, max_length=120)
    status: Status = Status.applied
    source: str | None = Field(default=None, max_length=50)
    url: str | None = Field(default=None, max_length=500)
    stack: list[str] = Field(default_factory=list)
    applied_at: date = Field(default_factory=date.today)
    notes: str | None = None

    @field_validator("stack")
    @classmethod
    def normalize_stack(cls, v: list[str]) -> list[str]:
        return _normalize_stack(v)


class ApplicationCreate(ApplicationBase):
    pass


class ApplicationUpdate(BaseModel):
    company: str | None = Field(default=None, min_length=1, max_length=120)
    position: str | None = Field(default=None, min_length=1, max_length=120)
    status: Status | None = None
    source: str | None = Field(default=None, max_length=50)
    url: str | None = Field(default=None, max_length=500)
    stack: list[str] | None = None
    applied_at: date | None = None
    notes: str | None = None

    @field_validator("stack")
    @classmethod
    def normalize_stack(cls, v: list[str] | None) -> list[str] | None:
        return None if v is None else _normalize_stack(v)


class ApplicationRead(ApplicationBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class TechCount(BaseModel):
    name: str
    count: int


class Stats(BaseModel):
    total: int
    by_status: dict[str, int]
    top_technologies: list[TechCount]
