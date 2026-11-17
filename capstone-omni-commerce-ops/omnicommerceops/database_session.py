"""SQLite engine and session management."""

import os
from pathlib import Path

from sqlalchemy import event
from sqlmodel import Session, SQLModel, create_engine

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATABASE_PATH = PROJECT_ROOT / "data" / "retailops_two_round.db"


def get_engine(database_path: Path | None = None, echo: bool = False):
    """Connect to the new RetailOps database, or a selected disposable one."""
    selected_path = Path(database_path or os.environ.get("OMNICOMMERCEOPS_DATABASE_PATH") or DATABASE_PATH)
    selected_path.parent.mkdir(parents=True, exist_ok=True)
    engine = create_engine(
        f"sqlite:///{selected_path}",
        echo=echo,
        connect_args={"check_same_thread": False},
    )

    @event.listens_for(engine, "connect")
    def enable_foreign_keys(connection, _connection_record):
        cursor = connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    return engine


def create_all_tables(engine=None) -> None:
    """Create all database tables from SQLModel metadata."""
    engine = engine or get_engine()
    SQLModel.metadata.create_all(engine)


def get_session(engine=None) -> Session:
    """Yield a database session (caller manages lifecycle)."""
    engine = engine or get_engine()
    return Session(engine)
