"""The two-round exercise has one reproducible starting state."""

from datetime import date

from sqlmodel import Session, SQLModel, select

from omnicommerceops.database_models import (
    Campaign,
    DemandScenario,
    Product,
    RegionalStock,
    RoundCase,
    SalesOutcome,
)
from omnicommerceops.seed_data import seed_baseline
from scripts.reset_database_seed import reset_database


def test_baseline_has_two_rounds_and_three_scenarios_per_case(engine):
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        seed_baseline(session)
        cases = session.exec(select(RoundCase)).all()
        scenarios = session.exec(select(DemandScenario)).all()
        assert {case.round_number for case in cases} == {1, 2}
        assert len(cases) == 6
        assert len(scenarios) == 18
        assert all(
            sum(item.selected_for_run for item in scenarios if item.round_case_id == case.id) == 1
            for case in cases
        )
        assert session.exec(select(SalesOutcome)).all() == []


def test_seeded_campaign_examples_and_long_lead_order_are_possible(engine):
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        seed_baseline(session)
        campaigns = session.exec(select(Campaign)).all()
        cases = {case.id: case for case in session.exec(select(RoundCase)).all()}
        assert {(cases[item.round_case_id].product_key, cases[item.round_case_id].round_number) for item in campaigns} == {
            ("PROD_COLA", 1), ("PROD_OJ", 1), ("PROD_CHIPS", 2)
        }
        stocks = {stock.product_key: stock for stock in session.exec(select(RegionalStock)).all()}
        assert stocks["PROD_CHIPS"].supplier_lead_days == 10
        assert date(2026, 1, 1).toordinal() + 10 > date(2026, 1, 7).toordinal()
        assert len(session.exec(select(Product)).all()) == 3


def test_seeding_fresh_database_twice_reproduces_opening_stock(engine):
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        seed_baseline(session)
        first = sorted((item.product_key, item.current_stock_units) for item in session.exec(select(RegionalStock)).all())
        for table in reversed(SQLModel.metadata.sorted_tables):
            session.exec(table.delete())
        session.commit()
        seed_baseline(session)
        second = sorted((item.product_key, item.current_stock_units) for item in session.exec(select(RegionalStock)).all())
        assert first == second == [("PROD_CHIPS", 120), ("PROD_COLA", 100), ("PROD_OJ", 80)]


def test_explicit_reset_recreates_a_disposable_database(tmp_path):
    database_path = tmp_path / "retailops.db"
    reset_database(database_path)
    reset_database(database_path)
    from omnicommerceops.database_session import get_engine
    with Session(get_engine(database_path)) as session:
        assert len(session.exec(select(RoundCase)).all()) == 6
        assert session.exec(select(SalesOutcome)).all() == []
