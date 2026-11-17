# RetailOps codebase guide

Current implementation: two-round demand planning and promotion performance.
Read [README.md](README.md) for the user journey and API paths, and
[PROJECT_PROMPT.md](PROJECT_PROMPT.md) for the teaching problem.

## Storage and seed

`database_models.py` has seven tables: `product`, `regional_stock`,
`round_case`, `demand_scenario`, `supply_order`, `campaign`, and
`sales_outcome`. The `product` natural key identifies one product; regional
stock is unique by product/region and is shared by both work areas and rounds.
Each `round_case` is unique by product/region/round. A supply order, campaign,
and outcome are each at most one per case. Money is stored as Decimal-valued
SQLModel fields; unit counts are integers.

`seed_data.py` builds six cases, 18 LOW/MEDIUM/HIGH demand rows, and three
example campaigns from fixed Python data. One demand level is selected per
case and remains private until sales run. The database is
`data/retailops_two_round.db` by default; override it with
`OMNICOMMERCEOPS_DATABASE_PATH` or the reset CLI's `--database-path`. The
previous ignored `data/retail_database.db` is left alone. Startup calls
`create_all`, not reset; users must intentionally run
`scripts/reset_database_seed.py` to erase worked cases and reseed.

Older `data/business_exports/*.csv` (including 280 historical weekly metrics)
and `knowledge_playbooks/` are static learning artifacts. They are not seed
input, runtime tables, or live exports of the current two-round app. The live
CSV download is built separately from completed public API responses.

## Business rules

`retail_math.py` is pure and has no DB/HTTP imports. It defines:

```text
suggested_order = max(0, forecast + safety_stock - current_stock - incoming_due)
customer_demand = max(0, base_demand + campaign_demand_change if campaign else base_demand)
sales = min(customer_demand, stock_before_sales)
lost_sales = customer_demand - sales
forecast_error_units = customer_demand - forecast
forecast_error_percent = error_units / forecast × 100 (undefined if forecast = 0)
net_contribution = campaign_gross_profit - no_campaign_gross_profit - promotion_spend
```

The no-campaign comparison uses the same selected base demand and
stock-before-sales. Either actual or comparison sales can be stock-constrained;
the assessment marks this explicitly. Monetary calculations use Decimal with
cent rounding. Campaigns are planned/revised before a run; a commercial
decision is recorded once after the run.

`calculate_case_metrics` returns a frozen `CaseMetrics`: revenue growth,
sales volume growth, average selling price, gross margin, demand fill rate,
absolute forecast error, and estimated incremental promotion ROI, plus the
gross profit needed to verify margin. The [student guide](docs/claude_exercises.md#metric-formulas)
defines each formula. Ratios use Decimal and two-decimal ROUND_HALF_UP rounding.
Undefined inputs/zero denominators return `None`; zero and negative results
remain valid. Forecast error uses customer demand and the saved forecast,
including when the GET request supplies a forecast preview. Gross profit
excludes promotion spend; incremental ROI divides net campaign contribution
by spend and differs from the historical SOP's revenue/spend return ratio.

`planning_service.py` persists forecast, chosen order, and reason. The order
has a due date based on supplier lead days. It does **not** change sellable
stock until `receive_supply_order` explicitly records a due receipt inside
the active period. Round 2 planning waits for round 1 to finish.

`round_service.py` requires all cases to have plans, the selling period to
have ended, and exactly one selected scenario per case. It commits all three
outcomes and stock reductions as one transaction. A second run returns a
conflict. `promotion_service.py` owns campaign plans, assessments, and one-time
decisions. Services use domain errors in `retail_exceptions.py`; `api_errors.py`
maps not-found to 404 and state conflicts to 409. Pydantic rejects malformed
or extra command fields with 422.

## Read path and UI

`case_queries.py` joins case/product/stock and constructs public views. A
pre-run view exposes only the min/max demand range, not the selected level or
`selected_for_run`. After the run it adds the immutable outcome, forecast
error, campaign assessment, and `analysis_metrics`. Metrics stay `null` before
sales. Round-2 growth joins the previous outcome by product and region; round 1
has no growth comparison. Unit costs come from the fixed product catalogue.
Case detail accepts a nonnegative forecast
query value to preview the server-calculated order suggestion without saving.
`api_schemas.py` is pure Pydantic, separate
from SQLModel storage; `api_routes.py` delegates to services and queries.
`api_dependencies.py` manages per-request sessions and startup table creation.

The Streamlit entry point is `ui/retail_dashboard.py`. Its planning and
promotion views call `RetailApiClient` methods, never database sessions.
The run button requires all three demand plans and explains that it reveals
demand and posts stock changes. Round 2 actions wait for round 1. Persona
labels are seeded identifiers, not security/authorization.

`ui/analysis_view.py` formats one selected-round table and one CSV download
without recalculating business metrics. `analysis_rows` flattens an explicit
field allowlist; `analysis_csv` uses standard-library csv/io. CSV includes only
completed cases through the selected round (up to six rows), sorted by round,
product, and region. It uses `SalesOutcome.stock_before_units`/`stock_after_units`
instead of mutable current stock. Missing values are empty CSV cells and `N/A`
in the table. Download data comes from the responses already read by the
dashboard; no endpoint, client method, dependency, or table was added.

The [two Claude exercises](docs/claude_exercises.md) guide external analysis,
manual calculation checks, and evidence-backed recommendations. They do not
introduce model calls, automatic optimization, or new playable rounds.

## Tests and limits

Run `uv run pytest tests/ -q` from this directory. Tests cover pure math,
deterministic seed/reset, planning/receipt, atomic sales, campaigns, HTTP
contracts, hidden-scenario protection, seven metric formulas, CSV contents,
historical stock stability, Streamlit analysis states, and a two-round journey. Use a
disposable path for reset tests; never reset a user's worked database during
routine verification. Run this project's suite separately from sibling
capstones because their `tests` and `ui` package names overlap.

For isolated test startup, set `OMNICOMMERCEOPS_DATABASE_PATH` to a temporary
path before running pytest: TestClient lifespan creates tables via the default
engine even when request sessions are overridden by in-memory test fixtures.

This is intentionally a toy educational product: no login, production
concurrency guarantee, real demand ingestion, CSV export endpoint, or embedded
AI workflow. Market share, turnover, carrying costs, transfers, and supplier
optimization remain extensions needing more data or workflows. A stale UI
submission may receive a 409 and should be refreshed.
