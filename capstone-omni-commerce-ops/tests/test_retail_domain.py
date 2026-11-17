"""Rules shared by both RetailOps work areas."""

from decimal import Decimal

import pytest

from omnicommerceops.retail_math import (
    assess_campaign,
    forecast_error,
    realize_sales,
    suggest_order_units,
)


def test_order_suggestion_accounts_for_stock_buffer_and_due_supply():
    assert suggest_order_units(90, 20, 40, 10) == 60
    assert suggest_order_units(20, 10, 40, 0) == 0


def test_sales_are_limited_by_stock_and_expose_lost_demand():
    outcome = realize_sales(130, 0, False, 100)
    assert (outcome.customer_demand_units, outcome.sales_volume_units, outcome.lost_sales_units) == (130, 100, 30)
    promoted = realize_sales(60, 20, True, 100)
    assert (promoted.customer_demand_units, promoted.sales_volume_units) == (80, 80)


def test_forecast_error_uses_customer_demand_and_handles_zero_forecast():
    assert forecast_error(50, 0).unit_difference == 50
    assert forecast_error(50, 0).percentage is None
    assert forecast_error(50, 100).percentage == Decimal("-50.00")


def test_campaign_estimates_incremental_profit_after_spend():
    result = assess_campaign(60, 20, 100, Decimal("10"), Decimal("9"), Decimal("4"), Decimal("20"))
    assert result.actual_gross_profit_usd == Decimal("400.00")
    assert result.comparison_gross_profit_usd == Decimal("360.00")
    assert result.net_contribution_usd == Decimal("20.00")
    assert result.stock_constrained is False


def test_baseline_stock_constraint_is_inconclusive_even_if_campaign_is_not():
    result = assess_campaign(110, -30, 100, Decimal("10"), Decimal("9"), Decimal("4"), Decimal("20"))
    assert result.stock_constrained is True


def test_negative_stock_is_rejected_but_signed_campaign_demand_is_valid():
    with pytest.raises(ValueError):
        realize_sales(20, 0, False, -1)
    assert realize_sales(20, -50, True, 10).customer_demand_units == 0


def _case_metrics(**overrides):
    from omnicommerceops import retail_math
    values = dict(forecast_volume_units=100, customer_demand_units=120,
                  sales_volume_units=90, gross_sales_revenue=Decimal("900"),
                  unit_wholesale_cost=Decimal("4"), marketing_promotion_spend=Decimal("20"),
                  net_contribution_usd=Decimal("-10"), previous_sales_volume_units=100,
                  previous_gross_sales_revenue=Decimal("1000"))
    return retail_math.calculate_case_metrics(**(values | overrides))


def test_case_metrics_calculates_seven_values():
    result = _case_metrics()
    assert result.gross_profit_usd == Decimal("540.00")
    assert result.revenue_growth_percentage == Decimal("-10.00")
    assert result.sales_volume_growth_percentage == Decimal("-10.00")
    assert result.average_selling_price_usd == Decimal("10.00")
    assert result.gross_margin_percentage == Decimal("60.00")
    assert result.demand_fill_rate_percentage == Decimal("75.00")
    assert result.absolute_forecast_error_percentage == Decimal("20.00")
    assert result.incremental_promotion_roi_percentage == Decimal("-50.00")


def test_case_metrics_zero_denominators_are_undefined():
    from dataclasses import asdict
    result = asdict(_case_metrics(
        forecast_volume_units=0, customer_demand_units=0, sales_volume_units=0,
        gross_sales_revenue=Decimal("0"), marketing_promotion_spend=Decimal("0"),
        previous_sales_volume_units=0, previous_gross_sales_revenue=Decimal("0"),
    ))
    assert result.pop("gross_profit_usd") == Decimal("0.00")
    assert all(value is None for value in result.values())


def test_case_metrics_preserves_zero_and_negative_results():
    unchanged = _case_metrics(previous_sales_volume_units=90, previous_gross_sales_revenue=Decimal("900"))
    assert unchanged.revenue_growth_percentage == Decimal("0.00")
    assert unchanged.sales_volume_growth_percentage == Decimal("0.00")
    empty = _case_metrics(sales_volume_units=0, gross_sales_revenue=Decimal("0"))
    assert empty.revenue_growth_percentage == Decimal("-100.00")
    assert empty.sales_volume_growth_percentage == Decimal("-100.00")
    loss = _case_metrics(unit_wholesale_cost=Decimal("12"))
    assert loss.gross_profit_usd == Decimal("-180.00")
    assert loss.gross_margin_percentage == Decimal("-20.00")
    overforecast = _case_metrics(customer_demand_units=50, sales_volume_units=50)
    assert overforecast.absolute_forecast_error_percentage == Decimal("50.00")


def test_case_metrics_missing_comparison_or_campaign():
    result = _case_metrics(previous_sales_volume_units=None, previous_gross_sales_revenue=None,
                           marketing_promotion_spend=None, net_contribution_usd=None)
    assert result.revenue_growth_percentage is None
    assert result.sales_volume_growth_percentage is None
    assert result.incremental_promotion_roi_percentage is None
    assert result.demand_fill_rate_percentage == Decimal("75.00")
    assert _case_metrics(marketing_promotion_spend=Decimal("0")).incremental_promotion_roi_percentage is None
    assert _case_metrics(net_contribution_usd=Decimal("0")).incremental_promotion_roi_percentage == Decimal("0.00")


def test_case_metrics_rounds_half_up():
    assert _case_metrics(gross_sales_revenue=Decimal("1.005"), sales_volume_units=1).average_selling_price_usd == Decimal("1.01")


@pytest.mark.parametrize("overrides", [
    {"forecast_volume_units": -1}, {"sales_volume_units": True},
    {"gross_sales_revenue": Decimal("NaN")}, {"unit_wholesale_cost": Decimal("-1")},
    {"marketing_promotion_spend": Decimal("-1")}, {"net_contribution_usd": Decimal("Infinity")},
])
def test_case_metrics_rejects_invalid_inputs(overrides):
    with pytest.raises(ValueError):
        _case_metrics(**overrides)
