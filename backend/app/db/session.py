"""Engine + session factory + the FastAPI ``get_db`` dependency."""
from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings

# ``pool_pre_ping`` quietly recycles connections dropped by Postgres / a proxy
# between requests, which is the usual cause of a first-request-after-idle 500.
# SQLite (used by the unit tests) ignores the pool kwargs.
_engine_kwargs: dict = {"pool_pre_ping": True, "future": True}
if settings.database_url.startswith("sqlite"):
    _engine_kwargs = {"future": True, "connect_args": {"check_same_thread": False}}

engine = create_engine(settings.database_url, **_engine_kwargs)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def get_db() -> Iterator[Session]:
    """Yield a request-scoped session and always close it afterwards."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
