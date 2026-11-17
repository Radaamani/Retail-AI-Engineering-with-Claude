# Make one retail decision with Claude

**Finish round 1, download its CSV, and start Exercise 1. Leave round 2 open.**

Your path: **Round 1 → promotion decision → inventory decision → round 2 → check the result.** Claude runs outside RetailOps; no model credentials are needed in the app.

## Get your round 1 CSV

1. Open RetailOps and select **Round 1**. If it has already run, go to step 3.
2. Save all three demand plans and run the sales period. For the starting example, use forecast **60**, chosen order **0**, and keep the seeded campaigns. Enter a reason for each plan.
3. Scroll to **Analysis** and select **Download analysis CSV**. Check that it contains three rows, all with `round_number = 1`.

**Keep your existing results.** If you need to restart the app, start only the API and Streamlit from [README](../README.md#start); skip its reset command. For a fresh exercise, use the disposable setup at the end of this guide.

Already completed round 2? Select round 1 to download its three-row file. Write your proposed decisions without changing saved plans. Then compare them with the decisions you actually made; do not treat completed round 2 as a fresh trial.

## Exercise 1 Decide whether to repeat a promotion

**Goal:** Recommend `REPEAT`, `ADJUST`, or `STOP` for Spark Cola in NORTH.

**Time:** About 8 minutes. **Input:** Your round-1 CSV.

### Do these three steps

1. Attach the CSV to Claude and paste the prompt below.
2. Check its calculation against the two cited CSV values.
3. Write your final decision and one reason. You may disagree with Claude.

```text
Use only round 1, product_key PROD_COLA, operating_region NORTH in this CSV.
Help me decide whether to REPEAT, ADJUST, or STOP its promotion.

Reply in exactly four short lines:
Decision: one recommendation.
Evidence: net_contribution_usd and marketing_promotion_spend from this row.
Check: show net_contribution_usd / marketing_promotion_spend * 100.
Limit: one uncertainty, including stock_constrained if relevant.

Treat promotion ROI as a simulated estimate. If spend is zero or campaign
values are missing, say ROI is unavailable. Do not invent causes or values.
```

**Expected output:** One decision supported by two numbers and one checked calculation.

**Done when:** You can explain the decision without reading Claude's response.

For the starting example, net contribution is **$20** and spend is **$20**. Check: `20 / 20 * 100 = 100%`. Different campaign decisions can produce different results. Revenue divided by spend is a different measure.

## Exercise 2 Choose one inventory action for round 2

**Goal:** Choose a forecast and order quantity for one product/region at risk of another stockout.

**Time:** About 12 minutes. **Input:** The same round-1 CSV. **Keep round 2 unplanned until you check the recommendation.**

### Do these three steps

1. Attach the CSV and paste the prompt below.
2. Check the order calculation. Review outstanding orders in the app; the CSV does not tell you which orders are still unreceived. If incoming supply differs from the assumed zero, ask Claude to recalculate before saving.
3. Write your chosen forecast, order quantity, and one reason. Check receipt timing before saving the plan.

```text
Use only round 1 in this RetailOps CSV. Choose the product/region with the
largest lost_sales_units; break ties using the lowest demand_fill_rate_percentage.
Recommend a round-2 forecast and order quantity for that one combination.

Reply in exactly four short lines:
Priority: product, region, and its lost sales or demand fill rate.
Plan: forecast units, order units, and a brief reason.
Check: max(0, forecast + safety_stock_units - stock_after_units - incoming_due).
Timing: explain whether the order can arrive during round 2 and one limitation.

Use incoming_due = 0 as an explicit assumption for this calculation; I will
check outstanding orders in the app. State that the forecast is an assumption.
The seeded round 2 runs January 8–14, 2026; orders are placed January 8.
Use supplier_lead_days to check arrival. Late or unreceived orders cannot sell.
Use customer_demand_units rather than constrained sales as evidence of demand.
If all cases had zero lost sales, say that no round-1 stockout was observed.
```

**Expected output:** One proposed plan, one worked order calculation, and a delivery check.

**Done when:** You can explain the order quantity and whether it can help during round 2. Identifying that supply arrives too late is a valid finding.

For example, forecast **100**, safety stock **20**, ending stock **30**, and incoming due **0** imply an order of `100 + 20 - 30 = 90`. An order placed January 8 with a ten-day lead time arrives January 18, after round 2 ends. Ordering alone does not prevent that period's stockout.

## Apply one decision and check the result

1. Select **Round 2**. Save the chosen product's forecast and order with your reason. Complete plans for the other two products.
2. Record any eligible stock receipts you choose to receive. An order is not sellable until explicitly received.
3. Run round 2. Download its CSV; it should contain six rows covering both rounds.
4. Compare your chosen product's demand fill rate and lost sales across rounds. Write **what changed**, **what did not**, and **one reason or uncertainty**.

**Done when:** You can connect your decision, delivery timing, and observed result. Demand differs between rounds, so this comparison does not prove your action caused every change.

Optional executive-summary follow-up: attach the six-row CSV and ask Claude, **“Give three short bullets: the largest revenue decline, the weakest promotion, and one next action. If nothing declined, say so. Identify each product, region, and round; cite figures and distinguish observations from hypotheses.”** Check the figures before sharing the summary.

## Submit your work

- The CSV used for each exercise and your exact prompt.
- Claude's four-line response and your final decision.
- One calculation you checked, with a correction if needed.
- Your round-2 comparison, or a comparison with previously saved decisions if both rounds were already complete.

## Reference Use only when you need it

### New disposable exercise

From the capstone directory, create a separate database and start the API in **Terminal 1**. Use an unused port if 8000 is already occupied.

```bash
analysis_demo_dir=$(mktemp -d /tmp/retailops-demo.XXXXXX)
uv run python scripts/reset_database_seed.py --database-path "$analysis_demo_dir/retailops.db"
OMNICOMMERCEOPS_DATABASE_PATH="$analysis_demo_dir/retailops.db" uv run uvicorn omnicommerceops.api_app:app --port 8000
```

In **Terminal 2**, from the same capstone directory:

```bash
uv run streamlit run ui/retail_dashboard.py --server.port 8501
```

If the API uses another port, set `RETAILOPS_API_URL` for Streamlit to match, as described in [README](../README.md#start). Use README's `uv sync --group dev` step if dependencies have not been installed.

### Metric formulas

Start with promotion ROI in Exercise 1 and demand fill rate in Exercise 2. Use the other metrics when a question needs them. Growth compares the same product and region in round 2 against round 1.

| Metric | Calculation |
| --- | --- |
| Revenue growth % | `(current revenue - previous revenue) / previous revenue * 100` |
| Sales volume growth % | `(current units sold - previous units sold) / previous units sold * 100` |
| Average selling price ($) | `gross_sales_revenue / sales_volume_units` |
| Gross margin % | `gross_profit_usd / gross_sales_revenue * 100` |
| Demand fill rate % | `sales_volume_units / customer_demand_units * 100` |
| Absolute forecast error % | `abs(customer_demand_units - forecast_volume_units) / forecast_volume_units * 100` |
| Estimated promotion ROI % | `net_contribution_usd / marketing_promotion_spend * 100` |

Gross profit is revenue minus units sold times unit wholesale cost. It excludes promotion spend. Net campaign contribution is actual gross profit minus the no-campaign comparison gross profit minus promotion spend.

Forecast **100** and demand **120** give **20%** absolute forecast error. Selling **90** against demand **120** gives **75%** fill rate. Contribution **-$10** with spend **$20** gives **-50%** estimated ROI.

Empty CSV cells mean unavailable/undefined, shown as `N/A` in the app. Zero denominators produce `N/A`; a real zero stays zero. Negative growth, margin, and ROI are valid. Absolute forecast error is not forecast accuracy; unit demand fill rate is not order fulfillment or service level.

### Limits to remember

- Demand and campaign demand changes are preset. The app does not learn demand effects from price or spend; promotion comparisons use the same base demand and stock.
- Each product appears in one region, so these observations cannot separate product effects from regional effects or establish competitor/seasonal causes.
- Stock before/after sales is recorded per round. Use the latest ending stock for planning; do not add stock across rounds. Remaining stock alone does not prove overstock.
- Historical CSVs in `data/business_exports/` and SOPs in `knowledge_playbooks/` are separate exercises. Their revenue/spend ratio and thresholds are different from this incremental promotion ROI.
- The app has two playable rounds. Further scenarios, market share, turnover, carrying costs, transfers, and supplier optimization require additional data or workflows. Any hypothetical impact needs explicit assumptions.
