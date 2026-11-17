# RetailOps — project prompt

Use this brief to onboard developers, business participants, and AI coding
assistants. The current product is an educational retail/FMCG application, not
a storefront or a historical-metrics dashboard.

## Business problem

A retailer must decide how much stock to order and whether a promotion was
worth running. Demand is uncertain; supplier deliveries are not instantly
sellable; promotions can change demand but also lower unit margin and incur
spend. A demand planner and a category manager work against the **same** stock
and sales truth across two periods.

The app seeds three cases in each of two rounds: cola/NORTH, orange juice/SOUTH,
and chips/WEST. Each case has LOW, MEDIUM, and HIGH demand scenarios. One level
is preset for the run but remains hidden until the round is posted. There is no
runtime random draw. Round 2 carries forward round-1 stock; explicit receipts
can add to it. A reset restores precisely the same baseline.

## Business-user experience

The Streamlit app has two work areas, not a role switcher:

- **Demand Planning** (`demand_planner`): see stock, safety stock, lead time and
  demand range; enter forecast, chosen order and reason; receive due orders;
  compare forecast with actual demand after the run.
- **Promotion Performance** (`category_manager`): set campaign price, spend and
  reason; after the run compare actual gross profit with the same scenario's
  no-campaign counterfactual, subtract spend, see any stock-constraint warning,
  then record `REPEAT`, `ADJUST`, or `STOP` with a reason.

The round run is one intentional action after all three demand plans exist.
It atomically records three immutable sales outcomes and reduces shared stock.
The app has no login, CSV endpoint, production approvals, or AI runtime yet.

An **Analysis** section below both work areas shows seven calculated metrics
for the selected completed round. One CSV button downloads completed cases
through that round. Students use this live file with the two guided
[Claude exercises](docs/claude_exercises.md): sales insights/executive reporting
and demand/inventory recommendations. Analysis uses existing API responses
and adds no decision workflow or database tables.

## Technical design

The application is the source of truth. Seven tables are `product`,
`regional_stock`, `round_case`, `demand_scenario`, `supply_order`, `campaign`,
and `sales_outcome`. SQLModel models describe storage; Pydantic models describe
HTTP payloads. `retail_math.py` contains pure business formulas. Services own
database transitions, routes are thin, and Streamlit uses the API through
`ui/http_api_client.py`. Invalid transitions use stable domain error codes.

Business vocabulary should stay explicit: `forecast_volume_units`,
`chosen_order_units`, `current_stock_units`, `customer_demand_units`,
`sales_volume_units`, `marketing_promotion_spend`, and
`net_contribution_usd`. Clients submit decisions, not selected scenarios,
sales totals, or campaign contribution. The no-campaign comparison uses the
**same revealed base demand and stock-before-sales**, not a different draw.

## Learning materials and future AI work

`data/business_exports/` contains older Excel-ready CSV exercises, including
the 280-row weekly metrics file. `knowledge_playbooks/` contains older SOPs.
These are preserved historical learning materials; they are **not** live
exports, current database seed input, or guaranteed to match the six-case
exercise. Business users can still use them in Excel or ChatGPT Web as separate
data exercises. These historical files remain separate from the current live
Analysis download.

AI engineering should extend this functioning product later, without making
AI a prerequisite for basic workflow execution. See [README.md](README.md)
for startup and public API paths, and [CODEBASE_GUIDE.md](CODEBASE_GUIDE.md)
for implementation and test details.
