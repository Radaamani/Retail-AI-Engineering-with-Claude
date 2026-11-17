"""FastAPI dependency injection and application lifecycle."""

from contextlib import asynccontextmanager

from sqlmodel import Session

from omnicommerceops.database_session import create_all_tables, get_engine, get_session


def get_db():
    """Yield a database session per request."""
    session = get_session()
    try:
        yield session
    finally:
        session.close()


@asynccontextmanager
async def lifespan(app):
    create_all_tables(get_engine())
    yield
