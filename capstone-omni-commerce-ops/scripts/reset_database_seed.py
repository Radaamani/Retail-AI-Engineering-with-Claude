"""Explicitly restore the deterministic two-round RetailOps baseline."""

import argparse
from pathlib import Path

from sqlmodel import Session, SQLModel

import omnicommerceops.database_models  # noqa: F401 - register tables
from omnicommerceops.database_session import get_engine
from omnicommerceops.seed_data import seed_baseline


def reset_database(database_path: Path | None = None) -> None:
    """Replace records only in the selected RetailOps database."""
    engine = get_engine(database_path)
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        seed_baseline(session)
    engine.dispose()


def main() -> None:
    parser = argparse.ArgumentParser(description="Reset two-round RetailOps exercise data")
    parser.add_argument("--database-path", type=Path, help="SQLite file to reset instead of the default")
    arguments = parser.parse_args()
    reset_database(arguments.database_path)
    print("Restored six RetailOps cases across two rounds")


if __name__ == "__main__":
    main()
