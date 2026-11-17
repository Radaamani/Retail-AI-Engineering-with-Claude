"""Demand plans, incoming orders, and explicit stock receipts."""

from datetime import date, timedelta

from sqlalchemy import func
from sqlmodel import Session, select

from omnicommerceops.database_models import RegionalStock, RoundCase, SalesOutcome, SupplyOrder
from omnicommerceops.retail_exceptions import RetailConflictError, RetailNotFoundError


def _round_is_complete(session: Session, round_number: int) -> bool:
    total_cases = session.exec(
        select(func.count()).select_from(RoundCase).where(RoundCase.round_number == round_number)
    ).one()
    total_outcomes = session.exec(
        select(func.count()).select_from(SalesOutcome)
        .join(RoundCase, SalesOutcome.round_case_id == RoundCase.id)
        .where(RoundCase.round_number == round_number)
    ).one()
    return total_cases > 0 and total_cases == total_outcomes


def _stock_for(session: Session, round_case: RoundCase) -> RegionalStock:
    stock = session.exec(
        select(RegionalStock).where(
            RegionalStock.product_key == round_case.product_key,
            RegionalStock.operating_region == round_case.operating_region,
        )
    ).first()
    if stock is None:
        raise RetailNotFoundError("Regional stock not found", product_key=round_case.product_key)
    return stock


def incoming_units_due_by(session: Session, product_key: str, region: str, end_date: date) -> int:
    """Count due, unreceived supply across both rounds without treating it as stock."""
    amount = session.exec(
        select(func.coalesce(func.sum(SupplyOrder.ordered_units), 0))
        .join(RoundCase, SupplyOrder.round_case_id == RoundCase.id)
        .where(
            RoundCase.product_key == product_key,
            RoundCase.operating_region == region,
            SupplyOrder.due_date <= end_date,
            SupplyOrder.received_date.is_(None),
        )
    ).one()
    return int(amount)


def record_demand_plan(
    session: Session,
    case_id: int,
    forecast_volume_units: int,
    chosen_order_units: int,
    reason: str,
    planner_identifier: str,
) -> RoundCase:
    round_case = session.get(RoundCase, case_id)
    if round_case is None:
        raise RetailNotFoundError("Round case not found", case_id=case_id)
    if planner_identifier != "demand_planner":
        raise RetailConflictError("WRONG_PERSONA", "Only the demand planner records demand plans")
    if not reason.strip() or min(forecast_volume_units, chosen_order_units) < 0:
        raise RetailConflictError("INVALID_PLAN", "Forecast, order quantity, and reason must be valid")
    if round_case.forecast_volume_units is not None:
        raise RetailConflictError("PLAN_ALREADY_RECORDED", "This case already has a demand plan")
    if round_case.round_number == 2 and not _round_is_complete(session, 1):
        raise RetailConflictError("ROUND_ONE_OPEN", "Finish round 1 before planning round 2")
    if _round_is_complete(session, round_case.round_number):
        raise RetailConflictError("ROUND_ALREADY_RUN", "This sales period has already run")

    regional_stock = _stock_for(session, round_case)
    round_case.forecast_volume_units = forecast_volume_units
    round_case.chosen_order_units = chosen_order_units
    round_case.plan_reason = reason.strip()
    round_case.planner_identifier = planner_identifier
    session.add(round_case)
    if chosen_order_units:
        session.add(SupplyOrder(
            round_case_id=round_case.id,
            ordered_units=chosen_order_units,
            placed_date=round_case.planning_date,
            due_date=round_case.planning_date + timedelta(days=regional_stock.supplier_lead_days),
        ))
    try:
        session.commit()
    except Exception:
        session.rollback()
        raise
    session.refresh(round_case)
    return round_case


def receive_supply_order(
    session: Session,
    order_id: int,
    received_date: date,
    planner_identifier: str,
) -> SupplyOrder:
    order = session.get(SupplyOrder, order_id)
    if order is None:
        raise RetailNotFoundError("Supply order not found", order_id=order_id)
    if planner_identifier != "demand_planner":
        raise RetailConflictError("WRONG_PERSONA", "Only the demand planner records receipts")
    if order.received_date is not None:
        raise RetailConflictError("ORDER_ALREADY_RECEIVED", "This order has already been received")

    round_case = session.get(RoundCase, order.round_case_id)
    active_round = 2 if _round_is_complete(session, 1) else 1
    active_case = session.exec(
        select(RoundCase).where(
            RoundCase.product_key == round_case.product_key,
            RoundCase.operating_region == round_case.operating_region,
            RoundCase.round_number == active_round,
        )
    ).one()
    if _round_is_complete(session, active_round):
        raise RetailConflictError("ROUND_ALREADY_RUN", "No selling period remains open for receipt")
    if received_date < order.due_date or not (active_case.planning_date <= received_date <= active_case.selling_period_end_date):
        raise RetailConflictError("RECEIPT_DATE_INVALID", "Receipt must be due and within the open selling period")

    stock = _stock_for(session, round_case)
    stock.current_stock_units += order.ordered_units
    order.received_date = received_date
    order.received_by = planner_identifier
    session.add(stock)
    session.add(order)
    try:
        session.commit()
    except Exception:
        session.rollback()
        raise
    session.refresh(order)
    return order
