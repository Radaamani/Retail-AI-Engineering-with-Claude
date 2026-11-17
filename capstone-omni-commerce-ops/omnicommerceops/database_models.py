"""Physical SQLModel table entities for SQLite storage."""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import CheckConstraint, UniqueConstraint
from sqlmodel import Field, SQLModel


class Product(SQLModel, table=True):
    __tablename__ = "product"

    product_key: str = Field(primary_key=True, max_length=32)
    product_name: str = Field(max_length=128)
    product_category: str = Field(max_length=64)
    unit_retail_price: Decimal = Field(max_digits=12, decimal_places=2)
    unit_wholesale_cost: Decimal = Field(max_digits=12, decimal_places=2)


class RegionalStock(SQLModel, table=True):
    """Sellable stock shared by both new RetailOps work areas."""

    __tablename__ = "regional_stock"
    __table_args__ = (
        UniqueConstraint("product_key", "operating_region"),
        CheckConstraint("current_stock_units >= 0"),
        CheckConstraint("safety_stock_units >= 0"),
        CheckConstraint("supplier_lead_days >= 0"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    product_key: str = Field(foreign_key="product.product_key")
    operating_region: str
    current_stock_units: int
    safety_stock_units: int
    supplier_lead_days: int


class RoundCase(SQLModel, table=True):
    __tablename__ = "round_case"
    __table_args__ = (
        UniqueConstraint("product_key", "operating_region", "round_number"),
        CheckConstraint("round_number IN (1, 2)"),
        CheckConstraint("forecast_volume_units IS NULL OR forecast_volume_units >= 0"),
        CheckConstraint("chosen_order_units IS NULL OR chosen_order_units >= 0"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    product_key: str = Field(foreign_key="product.product_key")
    operating_region: str
    round_number: int
    planning_date: date
    selling_period_end_date: date
    forecast_volume_units: Optional[int] = None
    chosen_order_units: Optional[int] = None
    plan_reason: Optional[str] = None
    planner_identifier: Optional[str] = None


class DemandScenario(SQLModel, table=True):
    __tablename__ = "demand_scenario"
    __table_args__ = (
        UniqueConstraint("round_case_id", "demand_level"),
        CheckConstraint("base_demand_units >= 0"),
        CheckConstraint("demand_level IN ('LOW', 'MEDIUM', 'HIGH')"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    round_case_id: int = Field(foreign_key="round_case.id")
    demand_level: str
    base_demand_units: int
    campaign_demand_change_units: int
    selected_for_run: bool


class SupplyOrder(SQLModel, table=True):
    __tablename__ = "supply_order"
    __table_args__ = (UniqueConstraint("round_case_id"), CheckConstraint("ordered_units > 0"))

    id: Optional[int] = Field(default=None, primary_key=True)
    round_case_id: int = Field(foreign_key="round_case.id")
    ordered_units: int
    placed_date: date
    due_date: date
    received_date: Optional[date] = None
    received_by: Optional[str] = None


class Campaign(SQLModel, table=True):
    __tablename__ = "campaign"
    __table_args__ = (
        UniqueConstraint("round_case_id"),
        CheckConstraint("campaign_unit_retail_price > 0"),
        CheckConstraint("marketing_promotion_spend >= 0"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    round_case_id: int = Field(foreign_key="round_case.id")
    campaign_unit_retail_price: Decimal = Field(max_digits=12, decimal_places=2)
    marketing_promotion_spend: Decimal = Field(max_digits=12, decimal_places=2)
    plan_reason: str
    category_manager_identifier: str
    decision: Optional[str] = None
    decision_reason: Optional[str] = None
    decided_at: Optional[datetime] = None


class SalesOutcome(SQLModel, table=True):
    __tablename__ = "sales_outcome"
    __table_args__ = (
        UniqueConstraint("round_case_id"),
        CheckConstraint("customer_demand_units >= 0"),
        CheckConstraint("sales_volume_units >= 0"),
        CheckConstraint("lost_sales_units >= 0"),
        CheckConstraint("stock_before_units >= 0"),
        CheckConstraint("stock_after_units >= 0"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    round_case_id: int = Field(foreign_key="round_case.id")
    selected_demand_level: str
    customer_demand_units: int
    sales_volume_units: int
    lost_sales_units: int
    selling_unit_retail_price: Decimal = Field(max_digits=12, decimal_places=2)
    gross_sales_revenue: Decimal = Field(max_digits=12, decimal_places=2)
    stock_before_units: int
    stock_after_units: int
    run_timestamp: datetime
