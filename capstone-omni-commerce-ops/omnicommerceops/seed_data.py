"""Repeatable two-round training cases; no runtime randomness."""

from datetime import date
from decimal import Decimal

from sqlmodel import Session

from omnicommerceops.database_models import Campaign, DemandScenario, Product, RegionalStock, RoundCase


ROUND_DATES = {
    1: (date(2026, 1, 1), date(2026, 1, 7)),
    2: (date(2026, 1, 8), date(2026, 1, 14)),
}

CASE_DATA = (
    ("PROD_COLA", "Spark Cola 500ml", "NORTH", 100, 20, 2, 10.0, 4.0,
     (40, 60, 90), (45, 70, 110), 20, "MEDIUM", "HIGH"),
    ("PROD_OJ", "Fresh Orange Juice 1L", "SOUTH", 80, 10, 1, 10.0, 4.0,
     (30, 50, 70), (35, 60, 85), 20, "MEDIUM", "LOW"),
    ("PROD_CHIPS", "Classic Potato Chips", "WEST", 120, 15, 10, 6.0, 2.0,
     (30, 70, 130), (40, 80, 120), 25, "HIGH", "MEDIUM"),
)

EXAMPLE_CAMPAIGNS = {
    ("PROD_COLA", 1): (Decimal("9.00"), Decimal("20.00"), "Test incremental demand"),
    ("PROD_OJ", 1): (Decimal("8.00"), Decimal("40.00"), "Test discounted volume"),
    ("PROD_CHIPS", 2): (Decimal("5.00"), Decimal("10.00"), "Review stock-constrained demand"),
}


def seed_baseline(session: Session) -> None:
    """Insert the same unopened exercise into an empty database."""
    for (
        product_key, product_name, region, opening_stock, safety_stock, lead_days,
        price, cost, round_one_levels, round_two_levels, campaign_change,
        round_one_selected, round_two_selected,
    ) in CASE_DATA:
        session.add(Product(
            product_key=product_key,
            product_name=product_name,
            product_category="FMCG",
            unit_retail_price=price,
            unit_wholesale_cost=cost,
        ))
        session.add(RegionalStock(
            product_key=product_key,
            operating_region=region,
            current_stock_units=opening_stock,
            safety_stock_units=safety_stock,
            supplier_lead_days=lead_days,
        ))
        for round_number, level_values, selected_level in (
            (1, round_one_levels, round_one_selected),
            (2, round_two_levels, round_two_selected),
        ):
            planning_date, selling_period_end_date = ROUND_DATES[round_number]
            round_case = RoundCase(
                product_key=product_key,
                operating_region=region,
                round_number=round_number,
                planning_date=planning_date,
                selling_period_end_date=selling_period_end_date,
            )
            session.add(round_case)
            session.flush()
            for level, base_demand in zip(("LOW", "MEDIUM", "HIGH"), level_values):
                session.add(DemandScenario(
                    round_case_id=round_case.id,
                    demand_level=level,
                    base_demand_units=base_demand,
                    campaign_demand_change_units=campaign_change,
                    selected_for_run=(level == selected_level),
                ))
            campaign_example = EXAMPLE_CAMPAIGNS.get((product_key, round_number))
            if campaign_example:
                campaign_price, spend, reason = campaign_example
                session.add(Campaign(
                    round_case_id=round_case.id,
                    campaign_unit_retail_price=campaign_price,
                    marketing_promotion_spend=spend,
                    plan_reason=reason,
                    category_manager_identifier="category_manager",
                ))
    session.commit()
