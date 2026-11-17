"""Planner decisions record incoming supply separately from sellable stock."""

from datetime import date, datetime, timezone
from decimal import Decimal

import pytest
from sqlmodel import select

from omnicommerceops.database_models import RegionalStock, RoundCase, SalesOutcome, SupplyOrder
from omnicommerceops.planning_service import (
    incoming_units_due_by,
    receive_supply_order,
    record_demand_plan,
)
from omnicommerceops.retail_exceptions import RetailConflictError


def test_zero_order_is_recorded_without_creating_supply(retail_session, cola_case):
    record_demand_plan(retail_session, cola_case.id, 60, 0, "Enough stock", "demand_planner")
    retail_session.refresh(cola_case)
    assert cola_case.chosen_order_units == 0
    assert retail_session.exec(select(SupplyOrder)).all() == []


def test_order_is_not_stock_until_receipt(retail_session, cola_case):
    record_demand_plan(retail_session, cola_case.id, 90, 20, "Protect launch", "demand_planner")
    order = retail_session.exec(select(SupplyOrder).where(SupplyOrder.round_case_id == cola_case.id)).one()
    stock = retail_session.exec(select(RegionalStock).where(RegionalStock.product_key == "PROD_COLA")).one()
    assert order.due_date == date(2026, 1, 3)
    assert stock.current_stock_units == 100
    assert incoming_units_due_by(retail_session, "PROD_COLA", "NORTH", date(2026, 1, 7)) == 20
    with pytest.raises(RetailConflictError):
        receive_supply_order(retail_session, order.id, date(2026, 1, 2), "demand_planner")
    receive_supply_order(retail_session, order.id, order.due_date, "demand_planner")
    retail_session.refresh(stock)
    assert stock.current_stock_units == 120
    assert incoming_units_due_by(retail_session, "PROD_COLA", "NORTH", date(2026, 1, 7)) == 0
    with pytest.raises(RetailConflictError):
        receive_supply_order(retail_session, order.id, order.due_date, "demand_planner")
    retail_session.refresh(stock)
    assert stock.current_stock_units == 120


def test_plan_cannot_be_replaced_or_recorded_by_wrong_persona(retail_session, cola_case):
    with pytest.raises(RetailConflictError):
        record_demand_plan(retail_session, cola_case.id, 60, 0, "Incorrect role", "category_manager")
    record_demand_plan(retail_session, cola_case.id, 60, 0, "Opening plan", "demand_planner")
    with pytest.raises(RetailConflictError):
        record_demand_plan(retail_session, cola_case.id, 70, 10, "Second order", "demand_planner")


def test_round_two_plan_waits_for_round_one_completion(retail_session):
    second_round = retail_session.exec(select(RoundCase).where(RoundCase.round_number == 2)).first()
    with pytest.raises(RetailConflictError):
        record_demand_plan(retail_session, second_round.id, 60, 0, "Too early", "demand_planner")


def test_long_lead_order_remains_open_for_round_two(retail_session):
    chips = retail_session.exec(select(RoundCase).where(RoundCase.product_key == "PROD_CHIPS", RoundCase.round_number == 1)).one()
    record_demand_plan(retail_session, chips.id, 100, 20, "Long lead", "demand_planner")
    order = retail_session.exec(select(SupplyOrder).where(SupplyOrder.round_case_id == chips.id)).one()
    assert order.due_date == date(2026, 1, 11)
    assert incoming_units_due_by(retail_session, "PROD_CHIPS", "WEST", date(2026, 1, 7)) == 0
    assert incoming_units_due_by(retail_session, "PROD_CHIPS", "WEST", date(2026, 1, 14)) == 20
    for case in retail_session.exec(select(RoundCase).where(RoundCase.round_number == 1)).all():
        if case.id != chips.id:
            record_demand_plan(retail_session, case.id, 60, 0, "Baseline", "demand_planner")
        retail_session.add(SalesOutcome(
            round_case_id=case.id,
            selected_demand_level="MEDIUM",
            customer_demand_units=0,
            sales_volume_units=0,
            lost_sales_units=0,
            selling_unit_retail_price=Decimal("1.00"),
            gross_sales_revenue=Decimal("0.00"),
            stock_before_units=0,
            stock_after_units=0,
            run_timestamp=datetime(2026, 1, 7, tzinfo=timezone.utc),
        ))
    retail_session.commit()
    receive_supply_order(retail_session, order.id, date(2026, 1, 11), "demand_planner")
    assert order.received_date == date(2026, 1, 11)
