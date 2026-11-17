# Educational Analysis Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Use superpowers:subagent-driven-development only if the user explicitly chooses delegation. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Add seven transparent metrics, one live-results CSV download, and two guided Claude exercises to the existing educational capstone.

**Architecture:** Extend the existing pure math and public case response. Add one UI reporting module that displays server metrics and serializes completed public outcomes; existing API calls provide all data. Students use Claude externally.

**Tech Stack:** Existing Python, Decimal, SQLModel, Pydantic, FastAPI, Streamlit, pytest; standard-library csv/io.

**Spec:** [Educational analysis design](../specs/2026-11-15-educational-analysis-design.md). Read it and AGENTS.md, README.md, PROJECT_PROMPT.md, and CODEBASE_GUIDE.md before implementation.

## Global Constraints

- Add no dependencies, database tables, migrations, API endpoints, or AI runtime.
- Preserve both decision work areas, all existing command contracts, seed scenarios, and the 280-row historical exercise.
- Keep business formulas in `omnicommerceops/retail_math.py`; Streamlit reads application data only through `RetailApiClient`.
- Metrics are server-owned, read-only additions to existing case GET responses; request payloads stay unchanged.
- Before a case has a sales outcome, its `analysis_metrics` is `null`; do not read a selected demand scenario to calculate new metrics.
- Read-only analysis must not modify plans, campaigns, stock, or outcomes, or reset the user's database.
- Use Decimal arithmetic with two-decimal ROUND_HALF_UP rounding. Undefined numeric values are `None` in Python, `null` in JSON, `N/A` in the table, and empty cells in CSV.

All paths below are relative to `capstone-omni-commerce-ops/`; run commands there. At planning time this directory had no Git repository. At execution time it had an unborn master with user-staged files; implementation preserved that index and created no commits.

Before running any test command below, set `OMNICOMMERCEOPS_DATABASE_PATH` to a disposable startup path. Existing TestClient lifespans create tables through the default engine even when request sessions are overridden. Keep this environment override in the execution shell:

```bash
analysis_test_dir=$(mktemp -d /tmp/retailops-analysis-tests.XXXXXX)
export OMNICOMMERCEOPS_DATABASE_PATH="$analysis_test_dir/startup.db"
```

## Review Focus

1. Zero forecast, demand, revenue, spend, or prior-period values: undefined percentages must stay missing, while real zero/negative results stay visible (Task 1).
2. Forecast preview requests and unopened cases: analysis must use the persisted forecast after sales and expose nothing about hidden demand before sales (Task 2).
3. Round-2 stock changes and unordered cases: round-1 export stock must stay historical; growth must match product and region (Tasks 2 and 3).
4. No campaign, zero-spend campaigns, and stock-constrained campaigns: do not fabricate ROI or lose counterfactual context (Tasks 1–3).
5. Round 2 selected before it runs, plus CSV quoting: table availability and exported rows must be explicit, and zero/False/comma-containing values must survive serialization (Task 3).

## File map

| File | Responsibility |
| --- | --- |
| Modify `omnicommerceops/retail_math.py` | One result dataclass and one metric calculation function |
| Modify `omnicommerceops/api_schemas.py` | Read-only metric response contract |
| Modify `omnicommerceops/case_queries.py` | Resolve previous outcome and populate calculated metrics |
| Create `ui/analysis_view.py` | Flatten completed cases, CSV serialization, and Analysis presentation |
| Modify `ui/retail_dashboard.py` | Call Analysis after the existing work areas using already fetched responses |
| Modify `tests/test_retail_domain.py` | Formula and undefined-value coverage |
| Modify `tests/test_retail_api.py` | Public metric lifecycle and matching/preview coverage |
| Create `tests/test_analysis.py` | CSV, historical-stock, and Streamlit integration coverage |
| Create `docs/claude_exercises.md` | Two prompts, deliverables, examples, and verification checklist |
| Modify `README.md`, `PROJECT_PROMPT.md`, `CODEBASE_GUIDE.md` | Accurate feature descriptions and student entry point |

## Task 1: Add the seven pure metrics

**Files:** `omnicommerceops/retail_math.py`, `tests/test_retail_domain.py`.

**Interfaces:** Consumes Decimal-valued money and integer units, plus optional previous outcome/campaign values. Produces `CaseMetrics` with the eight fields/types defined in the spec, and this keyword-only function:

```python
def calculate_case_metrics(
    *, forecast_volume_units: int, customer_demand_units: int,
    sales_volume_units: int, gross_sales_revenue: Decimal,
    unit_wholesale_cost: Decimal,
    marketing_promotion_spend: Decimal | None = None,
    net_contribution_usd: Decimal | None = None,
    previous_sales_volume_units: int | None = None,
    previous_gross_sales_revenue: Decimal | None = None,
) -> CaseMetrics: ...
```

- [x] **1. Write failing numerical tests.** `test_case_metrics_calculates_seven_values` uses forecast=100, demand=120, sold=90, revenue=900, unit cost=4, spend=20, net contribution=-10, previous sold=100, previous revenue=1000. Assert gross profit=540.00, revenue growth=-10.00, volume growth=-10.00, ASP=10.00, margin=60.00, fill=75.00, absolute forecast error=20.00, ROI=-50.00 (Decimal values).
- [x] **2. Add boundary tests.** `test_case_metrics_zero_denominators_are_undefined` sets forecast/demand/sold/revenue/spend/prior values to zero and asserts all seven metrics are None, gross profit=0.00. `test_case_metrics_preserves_zero_and_negative_results` asserts unchanged prior results yield 0.00 growth, positive baseline to zero current yields -100.00 growth, and a loss-making sale preserves negative margin. `test_case_metrics_missing_comparison_or_campaign` checks absent prior values and no/zero-spend campaign yield None only for affected KPIs; zero contribution with positive spend yields 0.00 ROI. `test_case_metrics_rounds_half_up` checks revenue=1.005 and sold=1 produce ASP=1.01.
- [x] **3. Verify the tests fail.** Run `uv run pytest tests/test_retail_domain.py -q`; expect failures for the missing metric function/result.
- [x] **4. Implement the dataclass and function.** Follow the spec formulas, reuse existing forecast error calculation/validation, and keep any safe percentage helper private. Validate nonnegative integer quantities and finite money using existing helpers; negative net contribution is valid. Do not change existing formulas.
- [x] **5. Verify the pure rules.** Run `uv run pytest tests/test_retail_domain.py -q`; all existing and new domain tests must pass.

## Task 2: Expose metrics through the existing case responses

**Files:** `omnicommerceops/api_schemas.py`, `omnicommerceops/case_queries.py`, `tests/test_retail_api.py`.

**Interfaces:** Consumes Task 1's `calculate_case_metrics(...) -> CaseMetrics`. Produces `CaseMetricsResponse` (`ConfigDict(from_attributes=True)`) and `RoundCaseResponse.analysis_metrics: CaseMetricsResponse | None = None`. GET paths, `build_case_response(...)`, request bodies, and `RetailApiClient` signatures stay the same.

- [x] **1. Write lifecycle tests.** `test_case_metrics_appear_only_after_sales` asserts pre-run `analysis_metrics is None` with no hidden scenario fields. Record all three round-1 plans (forecast=60, order=0), run the round, and inspect cola: gross profit=400.00, ASP=9.00, margin=55.56, fill=100.00, absolute forecast error=33.33, ROI=100.00, both growth values=None. Extend forbidden-command-field parameterization with `analysis_metrics`.
- [x] **2. Write comparison and preview tests.** `test_round_two_metrics_match_previous_product_and_region` uses completed outcomes with different prior revenues across product/region keys (an extra same-product regional fixture if needed), and asserts growth uses the exact matching key rather than row order/product alone. `test_case_metrics_ignore_preview_forecast` gets a completed case with `forecast_volume_units=999` query parameter and asserts its analysis/error remain based on saved forecast=60. `test_analysis_reads_do_not_change_business_state` compares stored stock/plans/outcomes before and after list/detail reads.
- [x] **3. Verify tests fail.** Run `uv run pytest tests/test_retail_api.py -q`; failures must identify missing/null metrics or field rejection assertions.
- [x] **4. Implement the response path.** In `build_case_response`, only after an outcome exists, fetch the previous round's outcome joined by matching product/region and round number. Calculate the existing campaign assessment once and reuse it for the current response and ROI inputs. Use outcome sales/revenue and the saved forecast; never current stock or a preview value. Add metrics to the existing response only; no new service, route, or storage layer.
- [x] **5. Verify API and regression contracts.** Run `uv run pytest tests/test_retail_api.py tests/test_retail_domain.py tests/test_retail_journey.py -q`; all pass and earlier two-round behavior is preserved.

## Task 3: Add the Analysis section and one CSV download

**Files:** create `ui/analysis_view.py`, modify `ui/retail_dashboard.py`, create `tests/test_analysis.py`.

**Interfaces:** Consumes public JSON dictionaries from existing `RetailApiClient.list_round_cases`. Produces:

```python
def analysis_rows(cases: list[dict]) -> list[dict]: ...
def analysis_csv(cases: list[dict]) -> str: ...
def render_analysis(
    cases: list[dict], export_cases: list[dict], round_number: int,
) -> None: ...
```

`analysis_rows` filters out cases without outcomes, sorts and maps exactly the spec's ordered CSV columns. `analysis_csv` uses `csv.DictWriter`/`io.StringIO` with headers even for empty input. `render_analysis` displays selected-round rows and serializes export_cases; it performs formatting only, without business math or DB imports.

- [x] **1. Write CSV behavior tests.** For API-backed tests in the new module, define a local `client(retail_session)` fixture using TestClient and the existing get_db/get_clock overrides, with clock `datetime(2026, 1, 14, 18, tzinfo=timezone.utc)`; clear overrides in a finally block. `test_analysis_csv_exports_only_completed_public_results` parses the CSV via DictReader, asserts exact ordered headers, excludes an unopened case, and sorts shuffled inputs by round/product/region. `test_analysis_csv_preserves_missing_zero_and_quoted_values` checks a product name containing comma/quotes round-trips, valid zero stays `0`, False stays `False`, missing metrics/campaign comparisons are empty, and no campaign spend is `0`. Check exported values numerically with Decimal rather than imposing insignificant zero padding.
- [x] **2. Write history/context tests.** `test_analysis_export_uses_recorded_stock_after_later_round` runs both rounds against in-memory fixtures, alters live stock through those normal workflows, then asserts round-1 `stock_before_units`/`stock_after_units` remain unchanged in the export. Assert `current_stock_units` and selected scenario fields are absent. `test_analysis_export_retains_campaign_context` checks no-campaign, zero-spend, negative contribution, and stock-constrained assessment fields/ROI are preserved from API data.
- [x] **3. Write integration tests.** Reuse the AppTest-to-TestClient HTTP monkeypatch pattern from `tests/test_retail_journey.py`. `test_analysis_section_tracks_selected_round_and_download` checks baseline has an empty-state message and disabled download; after round 1 there are three table/export rows and round-1 growth displays `N/A`; selecting unopened round 2 leaves its table empty and the three-row download available; after round 2 its table has three rows and the download has six. Capture the public `st.download_button` arguments with a test spy if AppTest cannot inspect download data directly; assert MIME, filename, parsed row count, and payload contents. Existing planner preview interactions must continue to pass.
- [x] **4. Verify tests fail.** Run `uv run pytest tests/test_analysis.py -q`; expect failures for missing functions/UI behavior.
- [x] **5. Implement export formatting.** Define explicit `ANALYSIS_COLUMNS` in the spec order. Use a fixed allowlist, no dictionary dumps or formulas. Never replace zero/False with blanks through truthiness checks. Use empty string for None in CSV; use `N/A` only for the visible table. Preserve JSON numeric strings without converting through float.
- [x] **6. Implement the section and wiring.** Render product/region plus seven metrics below the existing tabs. Use the current `cases` for its table and `first_round` for a round-1 export; when round 2 is selected use `first_round + cases`. Do not fetch round 2 just to export round 1. Show **Download analysis CSV**, filename/MIME from the spec, explanatory scope caption, and disabled state when there are no completed rows. No additional round selector, charts, or third decision area.
- [x] **7. Verify behavior.** Run `uv run pytest tests/test_analysis.py tests/test_retail_journey.py -q`; all pass without network services or modifications to the user's SQLite files.

## Task 4: Write the two exercises and reconcile project documentation

**Files:** create `docs/claude_exercises.md`; modify `README.md`, `PROJECT_PROMPT.md`, `CODEBASE_GUIDE.md`.

**Interfaces:** Consumes the exact CSV field names, seven KPI definitions, download scope, and UI labels from Tasks 1–3. Produces two student walkthroughs requiring no Claude API integration.

- [x] **1. Write student instructions and prompts.** Use the spec's two exercises, submission requirements, and limitations. Include forecast=100/demand=120 -> absolute forecast error=20%, sold=90/demand=120 -> fill=75%, and contribution=-10/spend=20 -> estimated ROI=-50%. Explicitly distinguish revenue/spend return ratio, gross profit, and incremental promotion ROI. Do not apply historical SOP thresholds to this ROI.
- [x] **2. Include a reproducible baseline walkthrough.** On a new disposable seed, save forecast=60/order=0 for all round-1 cases, keep example campaigns, then run round 1. Cola should show revenue=720.00, gross profit=400.00, contribution=20.00, and ROI=100.00. Students then choose their own round-2 plans and download six rows. Explain their outputs may differ when their decisions differ. Any reset example must use `--database-path /tmp/retailops-analysis-demo.db` and a matching API environment override; never instruct resetting worked cases as a prerequisite.
- [x] **3. Update onboarding documents.** Link the student guide in README; describe the reporting section and one CSV download accurately; update statements that there are no downloads. Preserve no-AI-runtime/no-new-endpoint statements and the separation of static historical data/SOPs from live exports. Explain deferred metrics rather than claiming complete coverage of the original brief.
- [x] **4. Walk through the documents manually.** Confirm prompt field names exist in CSV, growth is only round 2 versus round 1, students are asked for evidence and assumptions, and recommendations distinguish customer demand from constrained sales. Check relative links resolve. Do not add prose snapshot tests.

## Final acceptance and handoff

- [x] Run `uv run pytest tests/ -q` from this capstone only. Require all existing and new tests to pass; report the actual count rather than a fixed target.
- [x] Exercise the documented UI states with Streamlit AppTest and the API/CSV flow on a file-backed temporary database: unopened baseline, completed round 1, selected unopened round 2, completed round 2. Verify row counts, N/A display, filename, and CSV payloads. A real-browser smoke check was attempted but local server binding is blocked by the sandbox; no browser result is claimed. User databases remained untouched.
- [x] Verify the live CSV has only completed outcomes and round-1 stock remains unchanged after round 2. Independently recompute one margin, fill rate, growth, forecast error, and campaign ROI from the exported inputs.
- [x] Confirm no edits to seed data, database models, dependencies, request contracts, the historical CSVs/SOPs, or user SQLite files; remove any temporary verification files/processes you created.
- [x] Report changed files, test evidence, student workflow, and the deliberate limits. Separate automated checks from manual Claude exercise verification; do not claim the model exercises were run without actually running them.

## Effort and execution order

Tasks 1 and 2: approximately 3–4 hours; Task 3: approximately 1–2 hours; Task 4: approximately 1–2 hours; integrated verification: approximately 1–2 hours, overlapping earlier checks. Target total: 6–10 developer hours. Implement sequentially in the current session because each task consumes the previous task's interfaces and this is a small teaching feature. Execution completed with 58 passing tests; see the verification record below.

## Execution verification

- Baseline: 37 tests passed. Each code task was tested RED before implementation and GREEN afterward.
- Final suite: 58 tests passed using the installed environment (`uv run --no-sync pytest tests/ -q`), a temporary `UV_CACHE_DIR`, and a temporary `OMNICOMMERCEOPS_DATABASE_PATH`.
- Independently recomputed all seven metrics from generated three-row and six-row CSV files using actual file-backed API results; round-1 CSV remained identical after round 2.
- Independent review found one documentation issue: returning students could follow the reset command. The guide now explicitly says to keep their database and skip reset; the disposable example is for a new exercise. Prose was manually reviewed, without snapshot tests.
- Hash audit confirmed both user databases, historical CSVs/SOPs, seed data, database models, and dependency files were unchanged.
- Net application growth: 178 lines across four existing files and one new file; tests grew by 313 lines.
- No Claude model exercise was executed; these are documented manual student activities. Browser launch was unavailable because the sandbox denied local server binding.
