"""Pydantic HTTP contracts, separate from persistent SQLModel rows."""

from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class DemandPlanRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    forecast_volume_units: int = Field(ge=0)
    chosen_order_units: int = Field(ge=0)
    reason: str = Field(min_length=1)
    planner_identifier: str


class CampaignPlanRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    campaign_unit_retail_price: Decimal = Field(gt=0)
    marketing_promotion_spend: Decimal = Field(ge=0)
    reason: str = Field(min_length=1)
    category_manager_identifier: str


class SupplyReceiptRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    received_date: date
    planner_identifier: str


class CampaignDecisionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    decision: Literal["REPEAT", "ADJUST", "STOP"]
    reason: str = Field(min_length=1)
    category_manager_identifier: str


class SalesOutcomeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    round_case_id: int
    selected_demand_level: str
    customer_demand_units: int
    sales_volume_units: int
    lost_sales_units: int
    selling_unit_retail_price: Decimal
    gross_sales_revenue: Decimal
    stock_before_units: int
    stock_after_units: int
    run_timestamp: datetime


class CampaignAssessmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    actual_customer_demand_units: int
    comparison_customer_demand_units: int
    actual_sales_volume_units: int
    comparison_sales_volume_units: int
    actual_gross_profit_usd: Decimal
    comparison_gross_profit_usd: Decimal
    net_contribution_usd: Decimal
    stock_constrained: bool


class CaseMetricsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    gross_profit_usd: Decimal
    revenue_growth_percentage: Decimal | None
    sales_volume_growth_percentage: Decimal | None
    average_selling_price_usd: Decimal | None
    gross_margin_percentage: Decimal | None
    demand_fill_rate_percentage: Decimal | None
    absolute_forecast_error_percentage: Decimal | None
    incremental_promotion_roi_percentage: Decimal | None


class RoundCaseResponse(BaseModel):
    id: int
    product_key: str
    product_name: str
    operating_region: str
    round_number: int
    planning_date: date
    selling_period_end_date: date
    current_stock_units: int
    safety_stock_units: int
    supplier_lead_days: int
    regular_unit_retail_price: Decimal
    unit_wholesale_cost: Decimal
    demand_range_low_units: int
    demand_range_high_units: int
    forecast_volume_units: int | None
    chosen_order_units: int | None
    plan_reason: str | None
    suggested_order_units: int | None
    incoming_units_due_by_period_end: int
    supply_order: dict | None
    campaign: dict | None
    sales_outcome: SalesOutcomeResponse | None
    campaign_assessment: CampaignAssessmentResponse | None
    forecast_error_units: int | None
    forecast_error_percentage: Decimal | None
    permitted_actions: list[str]
    warning: str | None
    analysis_metrics: CaseMetricsResponse | None = None


class RoundRunResponse(BaseModel):
    round_number: int
    outcomes: list[SalesOutcomeResponse]


class ApiErrorBody(BaseModel):
    code: str
    message: str
    context: dict = Field(default_factory=dict)
