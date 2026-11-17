# Educational analysis design

## Purpose and agreed scope

Add the smallest useful bridge from the existing two-round RetailOps simulation to the two Tredence Claude use cases. Students run the product, download its results, analyze them with Claude, verify the analysis, and make a business recommendation. This design records the scope proposed in the conversation and requested for planning; implementation is a separate task.

Deliver two guided exercises, one CSV download, seven metrics, and one compact results table. Estimated implementation effort is 6–10 developer hours including tests and documentation. Application changes should remain roughly 200–350 lines; this is a sizing guide rather than an acceptance limit.

## Approaches and choice

| Approach | Tradeoff |
| --- | --- |
| Documentation using only historical CSVs | Smallest change, but students cannot analyze their own simulation decisions. |
| Existing API plus calculated metrics, CSV download, and external Claude exercises | Recommended scope from the conversation. Connects decisions to analysis while keeping the current architecture. |
| Embedded Claude assistant and expanded analytics services | Adds credentials, model failures, dependencies, and concepts beyond this teaching exercise. Defer. |

Use the second approach. The builder choices below keep it small: reuse existing GET responses, calculate metrics in pure Python, serialize CSV in the UI, and add a reporting section after the existing work areas.

## Global constraints

- Add no dependencies, database tables, migrations, API endpoints, or AI runtime.
- Preserve both decision work areas, all existing command contracts, seed scenarios, and the 280-row historical exercise.
- Keep business formulas in `omnicommerceops/retail_math.py`; Streamlit reads application data only through `RetailApiClient`.
- Metrics are server-owned, read-only additions to existing case GET responses; request payloads stay unchanged.
- Before a case has a sales outcome, its `analysis_metrics` is `null`; do not read a selected demand scenario to calculate new metrics.
- Read-only analysis must not modify plans, campaigns, stock, or outcomes, or reset the user's database.
- Use Decimal arithmetic with two-decimal ROUND_HALF_UP rounding. Undefined numeric values are `None` in Python, `null` in JSON, `N/A` in the table, and empty cells in CSV.

## Seven metrics and supporting value

Add one frozen `CaseMetrics` dataclass and a matching Pydantic `CaseMetricsResponse`. Both contain `gross_profit_usd: Decimal` and these seven `Decimal | None` fields:

| Field | Definition |
| --- | --- |
| `revenue_growth_percentage` | `(current revenue - previous revenue) / previous revenue * 100` |
| `sales_volume_growth_percentage` | `(current units sold - previous units sold) / previous units sold * 100` |
| `average_selling_price_usd` | `gross_sales_revenue / sales_volume_units` |
| `gross_margin_percentage` | `gross_profit_usd / gross_sales_revenue * 100` |
| `demand_fill_rate_percentage` | `sales_volume_units / customer_demand_units * 100` |
| `absolute_forecast_error_percentage` | `abs(customer_demand_units - forecast_volume_units) / forecast_volume_units * 100` |
| `incremental_promotion_roi_percentage` | `net_contribution_usd / marketing_promotion_spend * 100` |

`gross_profit_usd = gross_sales_revenue - sales_volume_units * unit_wholesale_cost`. This supporting value makes gross margin verifiable; it is not an eighth KPI. Read unit cost from the existing product record: product prices/costs have no editing workflow in this exercise. Historic cost versioning remains outside scope.

Growth exists only for a completed round-2 case with a completed round-1 case for the same `product_key` and `operating_region`. Round 1 has no prior-period comparison. Prior values must come from `SalesOutcome`, never current stock or list position.

Return undefined when a denominator is zero or required prior/campaign data is missing. Preserve valid negative growth, margin, and promotion ROI. Keep existing signed `forecast_error_percentage` intact. Use the persisted forecast, including when GET receives a preview forecast query parameter.

Gross profit excludes promotion spend. Promotion ROI uses the existing simulated same-demand, same-stock counterfactual; label it an estimate. Fill rate is unit demand fulfillment, not order fulfillment or service level. Absolute forecast error is not labelled forecast accuracy.

## API and presentation

Extend `RoundCaseResponse` with `analysis_metrics: CaseMetricsResponse | None = None`. `build_case_response` computes it after sales and reuses the existing campaign assessment once. No route/client method is needed.

Add `ui/analysis_view.py` to flatten public case dictionaries, serialize CSV with standard-library `csv`/`io`, and render the Analysis section below the two existing work areas. Table columns are product, region, and the seven metrics, for the selected round only. Use human-readable labels and `N/A` for missing values. Do not add charts, filters, aggregate KPI cards, or automated recommendations.

Provide one button labelled **Download analysis CSV**. For round 1, export its completed cases. For round 2, export completed cases from both rounds, using the first-round response already fetched by the dashboard. Thus unopened baseline yields no download, round 1 yields three rows, round 2 before sales still allows the three completed round-1 rows, and completed round 2 yields six rows. Explain that the download includes completed cases through the selected round. Selected-round table remains empty until that round runs.

CSV has one row per completed case, sorted by `(round_number, product_key, operating_region)`, with these exact ordered columns:

```text
round_number,case_id,product_key,product_name,operating_region,
forecast_volume_units,chosen_order_units,safety_stock_units,supplier_lead_days,
customer_demand_units,sales_volume_units,lost_sales_units,
stock_before_units,stock_after_units,selling_unit_retail_price,unit_wholesale_cost,
gross_sales_revenue,marketing_promotion_spend,comparison_gross_profit_usd,
net_contribution_usd,stock_constrained,gross_profit_usd,
revenue_growth_percentage,sales_volume_growth_percentage,average_selling_price_usd,
gross_margin_percentage,demand_fill_rate_percentage,
absolute_forecast_error_percentage,incremental_promotion_roi_percentage
```

Map `id` to `case_id`. Outcome values come from `sales_outcome`; campaign spend comes from `campaign`; comparison/contribution/constraint values come from `campaign_assessment`; computed values come from `analysis_metrics`. No campaign means zero promotion spend and empty campaign assessment/ROI cells. Preserve zero and `False` values. Never export `current_stock_units`, forecast previews, selected scenarios, or arbitrary dictionary fields. Record stock before/after the specific round instead. Use `retailops_analysis_through_round_{round_number}.csv`, MIME `text/csv`.

## Teaching materials

Create `docs/claude_exercises.md` with two copyable prompts and explicit submission requirements:

1. **Sales analysis:** compare round results, rank the observed product/region combinations, explain revenue/promotion performance, and produce a five-bullet executive summary plus two actions. Cite CSV rows and numbers; distinguish observations from hypotheses.
2. **Inventory analysis:** compare forecast with customer demand, rank stockout risk using lost sales/fill rate, review remaining stock against safety stock/lead time, and recommend next-round forecasts/orders with reasons. Require one worked calculation and a stakeholder summary.

Both exercises include a manual verification checklist, a small worked formula example, and guidance for `N/A`. Students submit the CSV, prompt, Claude output, and their corrected recommendation. Use Claude externally; model access and assessment of generated prose are manual classroom steps.

Explain that seeded demand is predetermined, campaign demand effects are preset rather than learned from spend/price, and the same product is not represented across multiple regions in the live exercise. Students cannot isolate regional causes or prove competitor/seasonal effects. Remaining stock alone does not prove excess inventory. Any suggested business impact must state assumptions; the project does not automatically rerun hypothetical scenarios.

Link the guide from README. Update README, PROJECT_PROMPT, and CODEBASE_GUIDE to describe the analysis/download features and preserve the distinction between live exports and historical CSVs/SOPs. The historical SOP's revenue/spend ratio is not the new incremental promotion ROI; do not apply its thresholds to the new KPI.

## Acceptance and deferred scope

The flow is: plan and run round 1, inspect/download three rows, plan and run round 2, inspect round-2 growth and download six rows, use the two prompts externally, then verify the answers. Existing workflows remain valid. Pure math, public API, CSV, historical-stock stability, and Streamlit integration receive targeted automated checks; prose exercises receive a manual walkthrough.

Market share, inventory turnover, carrying cost, stockout frequency over time, production service levels, inventory transfers, supplier optimization, embedded Claude, and automatic ranking/recommendation engines remain documented future work.
