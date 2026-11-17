"""Post one seeded sales period as one irreversible business event."""

from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy import and_, func
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from omnicommerceops.database_models import (
    Campaign, DemandScenario, Product, RegionalStock, RoundCase, SalesOutcome,
)
from omnicommerceops.planning_service import _round_is_complete
from omnicommerceops.retail_exceptions import RetailConflictError, RetailNotFoundError
from omnicommerceops.retail_math import realize_sales


def run_sales_period(session: Session, round_number: int, run_timestamp: datetime) -> list[SalesOutcome]:
    """Reveal demand, sell only available stock, and commit every case together."""
    if round_number not in (1, 2):
        raise RetailNotFoundError("Sales round not found", round_number=round_number)
    if round_number == 2 and not _round_is_complete(session, 1):
        raise RetailConflictError("ROUND_ONE_OPEN", "Finish round 1 before running round 2")

    case_count = session.exec(
        select(func.count()).select_from(RoundCase).where(RoundCase.round_number == round_number)
    ).one()
    if case_count == 0:
        raise RetailNotFoundError("Sales round not found", round_number=round_number)
    prior_outcome = session.exec(
        select(SalesOutcome.id)
        .join(RoundCase, SalesOutcome.round_case_id == RoundCase.id)
        .where(RoundCase.round_number == round_number)
    ).first()
    if prior_outcome is not None:
        raise RetailConflictError("ROUND_ALREADY_RUN", "This sales period has already run")

    statement = (
        select(RoundCase, Product, RegionalStock, DemandScenario, Campaign)
        .join(Product, RoundCase.product_key == Product.product_key)
        .join(RegionalStock, and_(
            RoundCase.product_key == RegionalStock.product_key,
            RoundCase.operating_region == RegionalStock.operating_region,
        ))
        .join(DemandScenario, and_(
            DemandScenario.round_case_id == RoundCase.id,
            DemandScenario.selected_for_run.is_(True),
        ))
        .outerjoin(Campaign, Campaign.round_case_id == RoundCase.id)
        .where(RoundCase.round_number == round_number)
        .order_by(RoundCase.id)
    )
    contexts = session.exec(statement).all()
    if len(contexts) != case_count or len({row[0].id for row in contexts}) != case_count:
        raise RetailConflictError("SCENARIO_INVALID", "Every case needs exactly one preset selected scenario")
    if any(round_case.forecast_volume_units is None for round_case, *_ in contexts):
        raise RetailConflictError("PLAN_MISSING", "Record a demand plan for every case before running sales")
    if any(run_timestamp.date() < round_case.selling_period_end_date for round_case, *_ in contexts):
        raise RetailConflictError("SALES_PERIOD_OPEN", "The selling period has not ended")

    outcomes: list[SalesOutcome] = []
    try:
        for round_case, product, stock, scenario, campaign in contexts:
            result = realize_sales(
                scenario.base_demand_units,
                scenario.campaign_demand_change_units,
                campaign is not None,
                stock.current_stock_units,
            )
            selling_price = Decimal(str(
                campaign.campaign_unit_retail_price if campaign else product.unit_retail_price
            ))
            revenue = (Decimal(result.sales_volume_units) * selling_price).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            outcome = SalesOutcome(
                round_case_id=round_case.id,
                selected_demand_level=scenario.demand_level,
                customer_demand_units=result.customer_demand_units,
                sales_volume_units=result.sales_volume_units,
                lost_sales_units=result.lost_sales_units,
                selling_unit_retail_price=selling_price,
                gross_sales_revenue=revenue,
                stock_before_units=stock.current_stock_units,
                stock_after_units=stock.current_stock_units - result.sales_volume_units,
                run_timestamp=run_timestamp,
            )
            stock.current_stock_units = outcome.stock_after_units
            session.add(stock)
            session.add(outcome)
            outcomes.append(outcome)
        session.commit()
    except IntegrityError as error:
        session.rollback()
        raise RetailConflictError("ROUND_ALREADY_RUN", "This sales period has already run") from error
    except Exception:
        session.rollback()
        raise
    for outcome in outcomes:
        session.refresh(outcome)
    return outcomes
