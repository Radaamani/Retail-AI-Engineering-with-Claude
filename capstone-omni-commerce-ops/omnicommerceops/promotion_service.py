"""Category-manager campaign plans and after-sales commercial decisions."""

from datetime import datetime
from decimal import Decimal
from typing import Literal

from sqlmodel import Session, select

from omnicommerceops.database_models import Campaign, DemandScenario, Product, RoundCase, SalesOutcome
from omnicommerceops.planning_service import _round_is_complete
from omnicommerceops.retail_exceptions import RetailConflictError, RetailNotFoundError
from omnicommerceops.retail_math import CampaignAssessment, assess_campaign


def _case(session: Session, case_id: int) -> RoundCase:
    round_case = session.get(RoundCase, case_id)
    if round_case is None:
        raise RetailNotFoundError("Round case not found", case_id=case_id)
    return round_case


def _campaign(session: Session, case_id: int) -> Campaign | None:
    return session.exec(select(Campaign).where(Campaign.round_case_id == case_id)).first()


def plan_campaign(
    session: Session,
    case_id: int,
    campaign_unit_retail_price: Decimal,
    marketing_promotion_spend: Decimal,
    reason: str,
    category_manager_identifier: str,
) -> Campaign:
    round_case = _case(session, case_id)
    if category_manager_identifier != "category_manager":
        raise RetailConflictError("WRONG_PERSONA", "Only the category manager plans campaigns")
    if round_case.round_number == 2 and not _round_is_complete(session, 1):
        raise RetailConflictError("ROUND_ONE_OPEN", "Finish round 1 before planning round 2")
    if session.exec(select(SalesOutcome.id).where(SalesOutcome.round_case_id == case_id)).first() is not None:
        raise RetailConflictError("ROUND_ALREADY_RUN", "Campaigns cannot change after sales")
    price = Decimal(str(campaign_unit_retail_price))
    spend = Decimal(str(marketing_promotion_spend))
    if not price.is_finite() or not spend.is_finite() or price <= 0 or spend < 0 or not reason.strip():
        raise RetailConflictError("INVALID_CAMPAIGN", "Campaign price, spend, and reason must be valid")

    campaign = _campaign(session, case_id)
    if campaign is None:
        campaign = Campaign(round_case_id=case_id)
    campaign.campaign_unit_retail_price = price
    campaign.marketing_promotion_spend = spend
    campaign.plan_reason = reason.strip()
    campaign.category_manager_identifier = category_manager_identifier
    session.add(campaign)
    try:
        session.commit()
    except Exception:
        session.rollback()
        raise
    session.refresh(campaign)
    return campaign


def get_campaign_assessment(session: Session, case_id: int) -> CampaignAssessment | None:
    _case(session, case_id)
    campaign = _campaign(session, case_id)
    outcome = session.exec(select(SalesOutcome).where(SalesOutcome.round_case_id == case_id)).first()
    if campaign is None or outcome is None:
        return None
    scenario = session.exec(select(DemandScenario).where(
        DemandScenario.round_case_id == case_id,
        DemandScenario.selected_for_run.is_(True),
    )).one()
    round_case = session.get(RoundCase, case_id)
    product = session.get(Product, round_case.product_key)
    return assess_campaign(
        scenario.base_demand_units,
        scenario.campaign_demand_change_units,
        outcome.stock_before_units,
        Decimal(str(product.unit_retail_price)),
        campaign.campaign_unit_retail_price,
        Decimal(str(product.unit_wholesale_cost)),
        campaign.marketing_promotion_spend,
    )


def record_campaign_decision(
    session: Session,
    case_id: int,
    decision: Literal["REPEAT", "ADJUST", "STOP"],
    reason: str,
    category_manager_identifier: str,
    decided_at: datetime,
) -> Campaign:
    _case(session, case_id)
    if category_manager_identifier != "category_manager":
        raise RetailConflictError("WRONG_PERSONA", "Only the category manager records campaign decisions")
    if decision not in ("REPEAT", "ADJUST", "STOP") or not reason.strip():
        raise RetailConflictError("INVALID_DECISION", "A decision and reason are required")
    campaign = _campaign(session, case_id)
    if campaign is None:
        raise RetailConflictError("CAMPAIGN_MISSING", "There is no campaign to decide")
    if session.exec(select(SalesOutcome.id).where(SalesOutcome.round_case_id == case_id)).first() is None:
        raise RetailConflictError("SALES_NOT_RUN", "Run sales before deciding on a campaign")
    if campaign.decision is not None:
        raise RetailConflictError("DECISION_ALREADY_RECORDED", "This campaign already has a decision")
    campaign.decision = decision
    campaign.decision_reason = reason.strip()
    campaign.decided_at = decided_at
    session.add(campaign)
    try:
        session.commit()
    except Exception:
        session.rollback()
        raise
    session.refresh(campaign)
    return campaign
