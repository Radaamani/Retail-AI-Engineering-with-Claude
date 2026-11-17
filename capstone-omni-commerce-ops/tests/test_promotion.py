"""Campaigns are planned before sales and judged after actual demand arrives."""

from datetime import datetime, timezone
from decimal import Decimal

import pytest
from sqlmodel import select

from omnicommerceops.database_models import Campaign, DemandScenario, RoundCase
from omnicommerceops.promotion_service import (
    get_campaign_assessment,
    plan_campaign,
    record_campaign_decision,
)
from omnicommerceops.retail_exceptions import RetailConflictError
from omnicommerceops.round_service import run_sales_period


RUN_TIME = datetime(2026, 1, 7, 18, tzinfo=timezone.utc)


def case_for(session, product_key):
    return session.exec(select(RoundCase).where(
        RoundCase.product_key == product_key,
        RoundCase.round_number == 1,
    )).one()


def test_campaign_can_be_revised_or_inserted_only_before_run(planned_round_one):
    session = planned_round_one
    cola = case_for(session, "PROD_COLA")
    revised = plan_campaign(session, cola.id, Decimal("9.50"), Decimal("15"), "Refined offer", "category_manager")
    assert revised.campaign_unit_retail_price == Decimal("9.50")
    assert len(session.exec(select(Campaign).where(Campaign.round_case_id == cola.id)).all()) == 1
    chips = case_for(session, "PROD_CHIPS")
    created = plan_campaign(session, chips.id, Decimal("5"), Decimal("10"), "Test offer", "category_manager")
    assert created.round_case_id == chips.id
    run_sales_period(session, 1, RUN_TIME)
    with pytest.raises(RetailConflictError):
        plan_campaign(session, cola.id, Decimal("8"), Decimal("20"), "Too late", "category_manager")


def test_post_run_assessment_compares_profit_at_pre_sales_stock(planned_round_one):
    session = planned_round_one
    cola = case_for(session, "PROD_COLA")
    orange_juice = case_for(session, "PROD_OJ")
    assert get_campaign_assessment(session, cola.id) is None
    run_sales_period(session, 1, RUN_TIME)
    profitable = get_campaign_assessment(session, cola.id)
    unprofitable = get_campaign_assessment(session, orange_juice.id)
    assert profitable.actual_gross_profit_usd == Decimal("400.00")
    assert profitable.comparison_gross_profit_usd == Decimal("360.00")
    assert profitable.net_contribution_usd == Decimal("20.00")
    assert profitable.stock_constrained is False
    assert unprofitable.net_contribution_usd == Decimal("-60.00")


def test_baseline_only_stock_constraint_is_inconclusive(planned_round_one):
    session = planned_round_one
    cola = case_for(session, "PROD_COLA")
    scenario = session.exec(select(DemandScenario).where(
        DemandScenario.round_case_id == cola.id,
        DemandScenario.selected_for_run.is_(True),
    )).one()
    scenario.base_demand_units = 110
    scenario.campaign_demand_change_units = -30
    session.add(scenario)
    session.commit()
    run_sales_period(session, 1, RUN_TIME)
    result = get_campaign_assessment(session, cola.id)
    assert result.stock_constrained is True
    assert result.actual_sales_volume_units == 80
    assert result.comparison_sales_volume_units == 100


def test_category_decision_requires_completed_campaign_and_is_one_time(planned_round_one):
    session = planned_round_one
    cola = case_for(session, "PROD_COLA")
    chips = case_for(session, "PROD_CHIPS")
    with pytest.raises(RetailConflictError):
        record_campaign_decision(session, cola.id, "REPEAT", "Too soon", "category_manager", RUN_TIME)
    run_sales_period(session, 1, RUN_TIME)
    with pytest.raises(RetailConflictError):
        record_campaign_decision(session, chips.id, "STOP", "No campaign", "category_manager", RUN_TIME)
    campaign = record_campaign_decision(session, cola.id, "REPEAT", "Positive estimate", "category_manager", RUN_TIME)
    assert campaign.decision == "REPEAT"
    assert campaign.decision_reason == "Positive estimate"
    with pytest.raises(RetailConflictError):
        record_campaign_decision(session, cola.id, "STOP", "Duplicate", "category_manager", RUN_TIME)
