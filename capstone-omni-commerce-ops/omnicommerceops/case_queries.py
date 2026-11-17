"""Public case views; the preset demand draw is private until sales run."""

from sqlalchemy import and_, func
from sqlmodel import Session, select

from omnicommerceops.api_schemas import RoundCaseResponse, RoundRunResponse, SalesOutcomeResponse
from omnicommerceops.database_models import Campaign, DemandScenario, Product, RegionalStock, RoundCase, SalesOutcome, SupplyOrder
from omnicommerceops.planning_service import _round_is_complete, incoming_units_due_by
from omnicommerceops.promotion_service import get_campaign_assessment
from omnicommerceops.retail_exceptions import RetailNotFoundError
from omnicommerceops.retail_math import calculate_case_metrics, forecast_error, suggest_order_units


def _context(session: Session, case_id: int):
    context = session.exec(
        select(RoundCase, Product, RegionalStock)
        .join(Product, RoundCase.product_key == Product.product_key)
        .join(RegionalStock, and_(
            RoundCase.product_key == RegionalStock.product_key,
            RoundCase.operating_region == RegionalStock.operating_region,
        ))
        .where(RoundCase.id == case_id)
    ).first()
    if context is None:
        raise RetailNotFoundError("Round case not found", case_id=case_id)
    return context


def build_case_response(
    session: Session, case_id: int, preview_forecast_volume_units: int | None = None
) -> RoundCaseResponse:
    round_case, product, stock = _context(session, case_id)
    low, high = session.exec(
        select(func.min(DemandScenario.base_demand_units), func.max(DemandScenario.base_demand_units))
        .where(DemandScenario.round_case_id == case_id)
    ).one()
    order = session.exec(select(SupplyOrder).where(SupplyOrder.round_case_id == case_id)).first()
    campaign = session.exec(select(Campaign).where(Campaign.round_case_id == case_id)).first()
    outcome = session.exec(select(SalesOutcome).where(SalesOutcome.round_case_id == case_id)).first()
    incoming = incoming_units_due_by(session, product.product_key, round_case.operating_region,
                                     round_case.selling_period_end_date)
    forecast_for_suggestion = (
        preview_forecast_volume_units if preview_forecast_volume_units is not None
        else round_case.forecast_volume_units
    )
    suggestion = None if forecast_for_suggestion is None else suggest_order_units(
        forecast_for_suggestion, stock.safety_stock_units, stock.current_stock_units, incoming
    )
    error = None if outcome is None or round_case.forecast_volume_units is None else forecast_error(
        outcome.customer_demand_units, round_case.forecast_volume_units
    )
    assessment = get_campaign_assessment(session, case_id) if outcome and campaign else None
    metrics = None
    if outcome is not None:
        previous = session.exec(
            select(SalesOutcome).join(RoundCase, SalesOutcome.round_case_id == RoundCase.id).where(
                RoundCase.product_key == round_case.product_key,
                RoundCase.operating_region == round_case.operating_region,
                RoundCase.round_number == round_case.round_number - 1,
            )
        ).first() if round_case.round_number == 2 else None
        metrics = calculate_case_metrics(
            forecast_volume_units=round_case.forecast_volume_units,
            customer_demand_units=outcome.customer_demand_units,
            sales_volume_units=outcome.sales_volume_units,
            gross_sales_revenue=outcome.gross_sales_revenue,
            unit_wholesale_cost=product.unit_wholesale_cost,
            marketing_promotion_spend=None if campaign is None else campaign.marketing_promotion_spend,
            net_contribution_usd=None if assessment is None else assessment.net_contribution_usd,
            previous_sales_volume_units=None if previous is None else previous.sales_volume_units,
            previous_gross_sales_revenue=None if previous is None else previous.gross_sales_revenue,
        )
    active = round_case.round_number == 1 or _round_is_complete(session, 1)
    actions = []
    if active and outcome is None:
        if round_case.forecast_volume_units is None:
            actions.append("record_demand_plan")
        actions.append("plan_campaign")
        if order is not None and order.received_date is None:
            actions.append("receive_supply_order")
    if campaign is not None and outcome is not None and campaign.decision is None:
        actions.append("record_campaign_decision")
    warning = None
    if order is not None and order.received_date is None:
        warning = "Ordered units are not sellable until explicitly received."
    return RoundCaseResponse(
        id=round_case.id, product_key=product.product_key, product_name=product.product_name,
        operating_region=round_case.operating_region, round_number=round_case.round_number,
        planning_date=round_case.planning_date, selling_period_end_date=round_case.selling_period_end_date,
        current_stock_units=stock.current_stock_units, safety_stock_units=stock.safety_stock_units,
        supplier_lead_days=stock.supplier_lead_days, regular_unit_retail_price=product.unit_retail_price,
        unit_wholesale_cost=product.unit_wholesale_cost, demand_range_low_units=low,
        demand_range_high_units=high, forecast_volume_units=round_case.forecast_volume_units,
        chosen_order_units=round_case.chosen_order_units, plan_reason=round_case.plan_reason,
        suggested_order_units=suggestion, incoming_units_due_by_period_end=incoming,
        supply_order=None if order is None else {
            "id": order.id, "ordered_units": order.ordered_units, "placed_date": order.placed_date,
            "due_date": order.due_date, "received_date": order.received_date,
        },
        campaign=None if campaign is None else {
            "campaign_unit_retail_price": campaign.campaign_unit_retail_price,
            "marketing_promotion_spend": campaign.marketing_promotion_spend,
            "plan_reason": campaign.plan_reason, "decision": campaign.decision,
            "decision_reason": campaign.decision_reason,
        },
        sales_outcome=None if outcome is None else SalesOutcomeResponse.model_validate(outcome),
        campaign_assessment=assessment, analysis_metrics=metrics,
        forecast_error_units=None if error is None else error.unit_difference,
        forecast_error_percentage=None if error is None else error.percentage,
        permitted_actions=actions, warning=warning,
    )


def build_round_run_response(session: Session, round_number: int, outcomes: list[SalesOutcome]) -> RoundRunResponse:
    return RoundRunResponse(round_number=round_number, outcomes=[
        SalesOutcomeResponse.model_validate(outcome) for outcome in outcomes
    ])
