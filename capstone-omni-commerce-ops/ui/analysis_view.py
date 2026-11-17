"""Display server-calculated metrics and export completed public case results."""

import csv
from io import StringIO

import streamlit as st


CASE_COLUMNS = (
    "round_number", "case_id", "product_key", "product_name", "operating_region",
    "forecast_volume_units", "chosen_order_units", "safety_stock_units", "supplier_lead_days",
)
OUTCOME_COLUMNS = (
    "customer_demand_units", "sales_volume_units", "lost_sales_units",
    "stock_before_units", "stock_after_units", "selling_unit_retail_price",
    "unit_wholesale_cost", "gross_sales_revenue",
)
ASSESSMENT_COLUMNS = ("comparison_gross_profit_usd", "net_contribution_usd", "stock_constrained")
METRIC_LABELS = {
    "revenue_growth_percentage": "Revenue growth %",
    "sales_volume_growth_percentage": "Sales volume growth %",
    "average_selling_price_usd": "Average selling price ($)",
    "gross_margin_percentage": "Gross margin %",
    "demand_fill_rate_percentage": "Demand fill rate %",
    "absolute_forecast_error_percentage": "Absolute forecast error %",
    "incremental_promotion_roi_percentage": "Estimated promotion ROI %",
}
ANALYSIS_COLUMNS = (
    *CASE_COLUMNS, *OUTCOME_COLUMNS, "marketing_promotion_spend", *ASSESSMENT_COLUMNS,
    "gross_profit_usd", *METRIC_LABELS,
)


def analysis_rows(cases: list[dict]) -> list[dict]:
    """Allowlisted fields only; stock comes from the outcome for that round."""
    rows = []
    for case in sorted(cases, key=lambda c: (c["round_number"], c["product_key"], c["operating_region"])):
        outcome = case["sales_outcome"]
        if outcome is None:
            continue
        assessment = case["campaign_assessment"] or {}
        metrics = case["analysis_metrics"] or {}
        row = {name: case["id"] if name == "case_id" else case[name] for name in CASE_COLUMNS}
        row.update({name: outcome[name] for name in OUTCOME_COLUMNS if name != "unit_wholesale_cost"})
        row["unit_wholesale_cost"] = case["unit_wholesale_cost"]
        row["marketing_promotion_spend"] = case["campaign"]["marketing_promotion_spend"] if case["campaign"] else 0
        row.update({name: assessment.get(name) for name in ASSESSMENT_COLUMNS})
        row.update({name: metrics.get(name) for name in ("gross_profit_usd", *METRIC_LABELS)})
        rows.append(row)
    return rows


def analysis_csv(cases: list[dict]) -> str:
    """CSV writes None as an empty cell, preserving real zeros and False."""
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=ANALYSIS_COLUMNS)
    writer.writeheader()
    writer.writerows(analysis_rows(cases))
    return output.getvalue()


def render_analysis(cases: list[dict], export_cases: list[dict], round_number: int) -> None:
    st.subheader("Analysis")
    rows = analysis_rows(cases)
    if rows:
        st.dataframe([
            {"Product": row["product_name"], "Region": row["operating_region"],
             **{label: "N/A" if row[name] is None else str(row[name]) for name, label in METRIC_LABELS.items()}}
            for row in rows
        ], hide_index=True)
    else:
        st.info("Run this sales period to see its analysis results.")
    st.caption("Growth compares round 2 with round 1 for the same product and region. "
               "N/A means missing inputs or a zero denominator. Promotion ROI is a simulated estimate.")
    st.caption("Download includes completed cases through the selected round. "
               "Analyze the CSV with Claude, then verify its conclusions against these results.")
    st.download_button(
        "Download analysis CSV", data=analysis_csv(export_cases),
        file_name=f"retailops_analysis_through_round_{round_number}.csv", mime="text/csv",
        disabled=not any(case["sales_outcome"] is not None for case in export_cases),
    )
