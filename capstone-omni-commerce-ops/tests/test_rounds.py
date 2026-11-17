"""A sales-period run posts all cases once and carries stock forward."""

from datetime import datetime, timezone

import pytest
from sqlmodel import select

from omnicommerceops.database_models import RegionalStock, RoundCase, SalesOutcome, SupplyOrder
from omnicommerceops.planning_service import record_demand_plan
from omnicommerceops.retail_exceptions import RetailConflictError
from omnicommerceops.round_service import run_sales_period


ROUND_ONE_CLOSE = datetime(2026, 1, 7, 18, tzinfo=timezone.utc)
ROUND_TWO_CLOSE = datetime(2026, 1, 14, 18, tzinfo=timezone.utc)


def test_round_two_cannot_run_before_round_one(retail_session):
    with pytest.raises(RetailConflictError):
        run_sales_period(retail_session, 2, ROUND_TWO_CLOSE)


def test_every_case_requires_a_plan_before_sales(retail_session):
    with pytest.raises(RetailConflictError):
        run_sales_period(retail_session, 1, ROUND_ONE_CLOSE)
    assert retail_session.exec(select(SalesOutcome)).all() == []


def test_high_demand_posts_once_and_open_order_remains_open(retail_session):
    cases = retail_session.exec(select(RoundCase).where(RoundCase.round_number == 1)).all()
    for case in cases:
        quantity = 20 if case.product_key == "PROD_CHIPS" else 0
        record_demand_plan(retail_session, case.id, 60, quantity, "Opening plan", "demand_planner")
    outcomes = run_sales_period(retail_session, 1, ROUND_ONE_CLOSE)
    chips_case = next(case for case in cases if case.product_key == "PROD_CHIPS")
    chips = next(item for item in outcomes if item.round_case_id == chips_case.id)
    assert (chips.customer_demand_units, chips.sales_volume_units, chips.lost_sales_units) == (130, 120, 10)
    assert chips.stock_after_units == 0
    order = retail_session.exec(select(SupplyOrder).where(SupplyOrder.round_case_id == chips_case.id)).one()
    assert order.received_date is None
    with pytest.raises(RetailConflictError):
        run_sales_period(retail_session, 1, ROUND_ONE_CLOSE)
    stock = retail_session.exec(select(RegionalStock).where(RegionalStock.product_key == "PROD_CHIPS")).one()
    assert stock.current_stock_units == 0


def test_round_two_sells_from_round_one_remaining_stock(planned_round_one):
    session = planned_round_one
    run_sales_period(session, 1, ROUND_ONE_CLOSE)
    cola_stock = session.exec(select(RegionalStock).where(RegionalStock.product_key == "PROD_COLA")).one()
    assert cola_stock.current_stock_units == 20
    for case in session.exec(select(RoundCase).where(RoundCase.round_number == 2)).all():
        record_demand_plan(session, case.id, 70, 0, "Learn from round one", "demand_planner")
    outcomes = run_sales_period(session, 2, ROUND_TWO_CLOSE)
    cola_case = session.exec(select(RoundCase).where(RoundCase.product_key == "PROD_COLA", RoundCase.round_number == 2)).one()
    cola = next(item for item in outcomes if item.round_case_id == cola_case.id)
    assert (cola.stock_before_units, cola.sales_volume_units, cola.lost_sales_units, cola.stock_after_units) == (20, 20, 90, 0)


def test_partial_failure_rolls_back_every_case(planned_round_one, monkeypatch):
    from omnicommerceops import round_service
    session = planned_round_one
    actual_rule = round_service.realize_sales
    calls = 0

    def fail_on_second_case(*arguments):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise RuntimeError("simulated posting failure")
        return actual_rule(*arguments)

    monkeypatch.setattr(round_service, "realize_sales", fail_on_second_case)
    with pytest.raises(RuntimeError, match="simulated posting failure"):
        run_sales_period(session, 1, ROUND_ONE_CLOSE)
    session.expire_all()
    assert session.exec(select(SalesOutcome)).all() == []
    stocks = {item.product_key: item.current_stock_units for item in session.exec(select(RegionalStock)).all()}
    assert stocks == {"PROD_COLA": 100, "PROD_OJ": 80, "PROD_CHIPS": 120}
