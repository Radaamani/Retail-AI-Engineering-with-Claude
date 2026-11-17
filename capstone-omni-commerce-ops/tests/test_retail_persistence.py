"""The baseline resets explicitly; ordinary startup keeps worked cases."""

from datetime import datetime, timezone

from sqlalchemy import func
from sqlmodel import Session, select

from omnicommerceops.database_models import DemandScenario, RegionalStock, RoundCase, SalesOutcome
from omnicommerceops.database_session import create_all_tables, get_engine
from omnicommerceops.planning_service import record_demand_plan
from omnicommerceops.round_service import run_sales_period
from scripts.reset_database_seed import reset_database


def _counts(database_path):
    engine = get_engine(database_path)
    with Session(engine) as session:
        return (
            session.exec(select(func.count()).select_from(RoundCase)).one(),
            session.exec(select(func.count()).select_from(DemandScenario)).one(),
            session.exec(select(func.count()).select_from(SalesOutcome)).one(),
            [row.current_stock_units for row in session.exec(select(RegionalStock).order_by(RegionalStock.product_key))],
        )


def test_explicit_reset_is_repeatable_and_startup_does_not_reset(tmp_path):
    database_path = tmp_path / "retailops.db"
    reset_database(database_path)
    opening = _counts(database_path)
    assert opening == (6, 18, 0, [120, 100, 80])
    reset_database(database_path)
    assert _counts(database_path) == opening

    engine = get_engine(database_path)
    with Session(engine) as session:
        for case in session.exec(select(RoundCase).where(RoundCase.round_number == 1)).all():
            record_demand_plan(session, case.id, 60, 0, "Exercise", "demand_planner")
        run_sales_period(session, 1, datetime(2026, 1, 14, tzinfo=timezone.utc))
    create_all_tables(get_engine(database_path))
    assert _counts(database_path)[2] == 3
    reset_database(database_path)
    assert _counts(database_path) == opening
