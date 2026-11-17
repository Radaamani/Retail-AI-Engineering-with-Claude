"""Pure retail formulas — no database, no HTTP, no side effects."""

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP


USD_CENT = Decimal("0.01")


@dataclass(frozen=True)
class SalesResult:
    customer_demand_units: int
    sales_volume_units: int
    lost_sales_units: int


@dataclass(frozen=True)
class ForecastError:
    unit_difference: int
    percentage: Decimal | None


@dataclass(frozen=True)
class CampaignAssessment:
    actual_customer_demand_units: int
    comparison_customer_demand_units: int
    actual_sales_volume_units: int
    comparison_sales_volume_units: int
    actual_gross_profit_usd: Decimal
    comparison_gross_profit_usd: Decimal
    net_contribution_usd: Decimal
    stock_constrained: bool


@dataclass(frozen=True)
class CaseMetrics:
    gross_profit_usd: Decimal
    revenue_growth_percentage: Decimal | None
    sales_volume_growth_percentage: Decimal | None
    average_selling_price_usd: Decimal | None
    gross_margin_percentage: Decimal | None
    demand_fill_rate_percentage: Decimal | None
    absolute_forecast_error_percentage: Decimal | None
    incremental_promotion_roi_percentage: Decimal | None


def _require_nonnegative_units(**quantities: int) -> None:
    if any(not isinstance(value, int) or isinstance(value, bool) or value < 0 for value in quantities.values()):
        raise ValueError("Quantities must be nonnegative integers")


def _money(value: Decimal) -> Decimal:
    amount = Decimal(str(value))
    if not amount.is_finite():
        raise ValueError("Money must be finite")
    return amount


def suggest_order_units(
    forecast_volume_units: int,
    safety_stock_units: int,
    current_stock_units: int,
    incoming_units_due_by_period_end: int,
) -> int:
    _require_nonnegative_units(
        forecast_volume_units=forecast_volume_units,
        safety_stock_units=safety_stock_units,
        current_stock_units=current_stock_units,
        incoming_units_due_by_period_end=incoming_units_due_by_period_end,
    )
    return max(0, forecast_volume_units + safety_stock_units - current_stock_units - incoming_units_due_by_period_end)


def realize_sales(
    base_demand_units: int,
    campaign_demand_change_units: int,
    campaign_active: bool,
    current_stock_units: int,
) -> SalesResult:
    _require_nonnegative_units(base_demand_units=base_demand_units, current_stock_units=current_stock_units)
    if not isinstance(campaign_demand_change_units, int) or isinstance(campaign_demand_change_units, bool):
        raise ValueError("Campaign demand change must be an integer")
    customer_demand_units = max(0, base_demand_units + (campaign_demand_change_units if campaign_active else 0))
    sales_volume_units = min(customer_demand_units, current_stock_units)
    return SalesResult(customer_demand_units, sales_volume_units, customer_demand_units - sales_volume_units)


def forecast_error(customer_demand_units: int, forecast_volume_units: int) -> ForecastError:
    _require_nonnegative_units(customer_demand_units=customer_demand_units, forecast_volume_units=forecast_volume_units)
    unit_difference = customer_demand_units - forecast_volume_units
    percentage = None if forecast_volume_units == 0 else (
        Decimal(unit_difference) / Decimal(forecast_volume_units) * 100
    ).quantize(USD_CENT, rounding=ROUND_HALF_UP)
    return ForecastError(unit_difference, percentage)


def _ratio(numerator, denominator, scale: int = 100) -> Decimal | None:
    """A missing input or zero denominator means the ratio is undefined."""
    if numerator is None or denominator is None or denominator == 0:
        return None
    return (Decimal(numerator) / Decimal(denominator) * scale).quantize(USD_CENT, rounding=ROUND_HALF_UP)


def calculate_case_metrics(
    *, forecast_volume_units: int, customer_demand_units: int,
    sales_volume_units: int, gross_sales_revenue: Decimal,
    unit_wholesale_cost: Decimal,
    marketing_promotion_spend: Decimal | None = None,
    net_contribution_usd: Decimal | None = None,
    previous_sales_volume_units: int | None = None,
    previous_gross_sales_revenue: Decimal | None = None,
) -> CaseMetrics:
    """Seven teaching metrics from recorded outcomes; no selected scenario needed."""
    _require_nonnegative_units(
        forecast_volume_units=forecast_volume_units, customer_demand_units=customer_demand_units,
        sales_volume_units=sales_volume_units,
    )
    if previous_sales_volume_units is not None:
        _require_nonnegative_units(previous_sales_volume_units=previous_sales_volume_units)
    revenue, cost = _money(gross_sales_revenue), _money(unit_wholesale_cost)
    spend = None if marketing_promotion_spend is None else _money(marketing_promotion_spend)
    contribution = None if net_contribution_usd is None else _money(net_contribution_usd)
    previous_revenue = None if previous_gross_sales_revenue is None else _money(previous_gross_sales_revenue)
    if any(value is not None and value < 0 for value in (revenue, cost, spend, previous_revenue)):
        raise ValueError("Revenue, unit cost, and promotion spend cannot be negative")
    gross_profit = (revenue - sales_volume_units * cost).quantize(USD_CENT, rounding=ROUND_HALF_UP)
    error = forecast_error(customer_demand_units, forecast_volume_units)
    return CaseMetrics(
        gross_profit_usd=gross_profit,
        revenue_growth_percentage=_ratio(
            None if previous_revenue is None else revenue - previous_revenue, previous_revenue,
        ),
        sales_volume_growth_percentage=_ratio(
            None if previous_sales_volume_units is None else sales_volume_units - previous_sales_volume_units,
            previous_sales_volume_units,
        ),
        average_selling_price_usd=_ratio(revenue, sales_volume_units, scale=1),
        gross_margin_percentage=_ratio(gross_profit, revenue),
        demand_fill_rate_percentage=_ratio(sales_volume_units, customer_demand_units),
        absolute_forecast_error_percentage=None if error.percentage is None else abs(error.percentage),
        incremental_promotion_roi_percentage=_ratio(contribution, spend),
    )


def assess_campaign(
    base_demand_units: int,
    campaign_demand_change_units: int,
    current_stock_units: int,
    unit_retail_price: Decimal,
    campaign_unit_retail_price: Decimal,
    unit_wholesale_cost: Decimal,
    marketing_promotion_spend: Decimal,
) -> CampaignAssessment:
    regular_price = _money(unit_retail_price)
    campaign_price = _money(campaign_unit_retail_price)
    cost = _money(unit_wholesale_cost)
    spend = _money(marketing_promotion_spend)
    if regular_price <= 0 or campaign_price <= 0 or cost < 0 or spend < 0:
        raise ValueError("Prices must be positive; cost and spend cannot be negative")
    actual = realize_sales(base_demand_units, campaign_demand_change_units, True, current_stock_units)
    comparison = realize_sales(base_demand_units, 0, False, current_stock_units)
    actual_gross_profit = (Decimal(actual.sales_volume_units) * (campaign_price - cost)).quantize(USD_CENT, rounding=ROUND_HALF_UP)
    comparison_gross_profit = (Decimal(comparison.sales_volume_units) * (regular_price - cost)).quantize(USD_CENT, rounding=ROUND_HALF_UP)
    return CampaignAssessment(
        actual_customer_demand_units=actual.customer_demand_units,
        comparison_customer_demand_units=comparison.customer_demand_units,
        actual_sales_volume_units=actual.sales_volume_units,
        comparison_sales_volume_units=comparison.sales_volume_units,
        actual_gross_profit_usd=actual_gross_profit,
        comparison_gross_profit_usd=comparison_gross_profit,
        net_contribution_usd=(actual_gross_profit - comparison_gross_profit - spend).quantize(USD_CENT, rounding=ROUND_HALF_UP),
        stock_constrained=(actual.lost_sales_units > 0 or comparison.lost_sales_units > 0),
    )
