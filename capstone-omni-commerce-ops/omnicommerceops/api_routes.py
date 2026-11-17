"""Thin HTTP adapters for the two-round RetailOps workflow."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select

from omnicommerceops.api_dependencies import get_db
from omnicommerceops.api_schemas import (
    CampaignDecisionRequest, CampaignPlanRequest, DemandPlanRequest,
    RoundCaseResponse, RoundRunResponse, SupplyReceiptRequest,
)
from omnicommerceops.case_queries import build_case_response, build_round_run_response
from omnicommerceops.database_models import RoundCase
from omnicommerceops.planning_service import record_demand_plan, receive_supply_order
from omnicommerceops.promotion_service import plan_campaign, record_campaign_decision
from omnicommerceops.retail_exceptions import RetailNotFoundError
from omnicommerceops.round_service import run_sales_period

router = APIRouter()


def get_clock() -> datetime:
    return datetime.now(timezone.utc)


@router.get("/rounds/{round_number}/cases", response_model=list[RoundCaseResponse])
def list_round_cases(round_number: int, session: Session = Depends(get_db)):
    if round_number not in (1, 2):
        raise RetailNotFoundError("Sales round not found", round_number=round_number)
    case_ids = session.exec(select(RoundCase.id).where(
        RoundCase.round_number == round_number
    ).order_by(RoundCase.id)).all()
    return [build_case_response(session, case_id) for case_id in case_ids]


@router.get("/cases/{case_id}", response_model=RoundCaseResponse)
def get_case(case_id: int, forecast_volume_units: int | None = Query(None, ge=0),
             session: Session = Depends(get_db)):
    return build_case_response(session, case_id, forecast_volume_units)


@router.post("/cases/{case_id}/demand-plan", response_model=RoundCaseResponse)
def save_demand_plan(case_id: int, payload: DemandPlanRequest, session: Session = Depends(get_db)):
    record_demand_plan(session, case_id, payload.forecast_volume_units, payload.chosen_order_units,
                       payload.reason, payload.planner_identifier)
    return build_case_response(session, case_id)


@router.put("/cases/{case_id}/campaign", response_model=RoundCaseResponse)
def save_campaign(case_id: int, payload: CampaignPlanRequest, session: Session = Depends(get_db)):
    plan_campaign(session, case_id, payload.campaign_unit_retail_price, payload.marketing_promotion_spend,
                  payload.reason, payload.category_manager_identifier)
    return build_case_response(session, case_id)


@router.post("/supply-orders/{order_id}/receipt", response_model=RoundCaseResponse)
def receive_order(order_id: int, payload: SupplyReceiptRequest, session: Session = Depends(get_db)):
    order = receive_supply_order(session, order_id, payload.received_date, payload.planner_identifier)
    return build_case_response(session, order.round_case_id)


@router.post("/rounds/{round_number}/run", response_model=RoundRunResponse)
def run_round(round_number: int, session: Session = Depends(get_db), now: datetime = Depends(get_clock)):
    outcomes = run_sales_period(session, round_number, now)
    return build_round_run_response(session, round_number, outcomes)


@router.post("/cases/{case_id}/campaign-decision", response_model=RoundCaseResponse)
def save_campaign_decision(case_id: int, payload: CampaignDecisionRequest,
                           session: Session = Depends(get_db), now: datetime = Depends(get_clock)):
    record_campaign_decision(session, case_id, payload.decision, payload.reason,
                             payload.category_manager_identifier, now)
    return build_case_response(session, case_id)
