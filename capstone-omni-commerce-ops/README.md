# RetailOps (OmniCommerceOps)

An educational retail product with two work areas—**Demand Planning** and
**Promotion Performance**—sharing one stock record per product and region.
Three seeded products move through two repeatable sales periods. The demand
planner forecasts, chooses an order and explicitly receives it; the category
manager plans a campaign and, after sales, records a commercial decision.
One deliberate sales-run action reveals preset demand and posts stock changes.

Business users work in the Streamlit app. Developers can read the business
rules in pure Python and extend the FastAPI product for later AI engineering
exercises. The application database is the source of truth. The older CSVs in
`data/business_exports/` and `knowledge_playbooks/` remain **static historical
learning artifacts**, not live app exports or the reset source.

## Start

From this directory:

```bash
uv sync --group dev
uv run python scripts/reset_database_seed.py  # explicit reset: erases worked RetailOps cases
uv run uvicorn omnicommerceops.api_app:app --reload --port 8000
```

In another terminal:

```bash
uv run streamlit run ui/retail_dashboard.py --server.port 8501
```

The new application uses `data/retailops_two_round.db`. The previous ignored
`data/retail_database.db` is not touched. Starting the API creates missing
tables but does not reset or seed cases. To verify safely against a disposable
database, pass `--database-path PATH` to the reset command and set
`OMNICOMMERCEOPS_DATABASE_PATH=PATH` for the API. If the API uses a nondefault
port, set `RETAILOPS_API_URL` for Streamlit (for example,
`http://127.0.0.1:8765`).

## Workflow

1. Select round 1. Review each case's stock, lead time, and low–high demand range.
2. Enter a forecast to preview the server-calculated order suggestion, then
   record one demand plan per case; optionally plan or revise campaigns.
3. Receive any due supply order explicitly. Ordered but unreceived units do not sell.
4. Run the sales period once. The selected demand level, sales, lost sales,
   forecast error, gross revenue, and remaining stock become visible.
5. Review campaign contribution against a no-campaign comparison, then record
   `REPEAT`, `ADJUST`, or `STOP` with a reason.
6. Plan and run round 2 from the carried stock. A fresh explicit reset restores
   the same unopened baseline.
7. Review **Analysis** below the work areas and select **Download analysis CSV**.
   The table shows the selected round; the file contains completed cases through
   that round (three rows after round 1, six after round 2).

After round 1, follow the two [Claude exercises](docs/claude_exercises.md) to
make one promotion decision and one inventory decision before planning round 2.
Apply a checked recommendation, then compare the results. An optional follow-up
produces a short executive summary. Students use Claude externally; RetailOps
requires no model credentials.

Analysis includes revenue/volume growth, average selling price, gross margin,
demand fill rate, absolute forecast error, and estimated incremental promotion
ROI. Growth compares the same product/region across rounds; missing inputs and
zero denominators show `N/A` (empty CSV cells). Historical round stock stays
fixed in the export even when later sales change current stock.

The dashboard shows seeded persona labels (`demand_planner` and
`category_manager`) rather than login or a role switcher. It is a training
product, not a production authorization system.

## Public API

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/rounds/{round_number}/cases` | Cases and current public state |
| GET | `/cases/{case_id}` | One case |
| POST | `/cases/{case_id}/demand-plan` | Forecast and order intent |
| PUT | `/cases/{case_id}/campaign` | Campaign plan or pre-run revision |
| POST | `/supply-orders/{order_id}/receipt` | Make due stock sellable |
| POST | `/rounds/{round_number}/run` | Post all cases' sales once |
| POST | `/cases/{case_id}/campaign-decision` | Post-run commercial decision |

`GET /cases/{case_id}?forecast_volume_units=N` previews an order suggestion
without saving a plan. The persisted forecast remains unchanged until the
demand-plan command is submitted.

Server-owned demand selection and calculated outcomes cannot be submitted by
clients. Before a run, case views expose only the low–high range, not the
selected scenario. Domain errors use `{code, message, context}`; invalid
request bodies return 422.

Case GET responses include read-only `analysis_metrics` after sales and `null`
before sales. Streamlit builds CSV downloads from these existing responses;
there is no separate export endpoint.

## Developer map

- `omnicommerceops/retail_math.py`: pure forecast, sales, and campaign rules.
- `database_models.py`, `seed_data.py`, `database_session.py`: seven SQLModel
  tables, deterministic cases, and SQLite persistence.
- `planning_service.py`, `round_service.py`, `promotion_service.py`: workflows.
- `case_queries.py`, `api_schemas.py`, `api_routes.py`: public views, Pydantic
  contracts, and thin HTTP adapters.
- `ui/`: two work areas behind `RetailApiClient`.
- `tests/`: pure, service, API, persistence, and full-journey coverage.

See [CODEBASE_GUIDE.md](CODEBASE_GUIDE.md) and
[PROJECT_PROMPT.md](PROJECT_PROMPT.md). Sibling capstones are
[BFSIHub](../bfsihub/) and [SupplyChainOps](../supplychainops/).

```bash
uv run pytest tests/ -q
```
