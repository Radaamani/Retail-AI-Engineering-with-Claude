"""The public RetailOps contract exposes intent, never the hidden demand draw."""

from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

from omnicommerceops.api_app import app
from omnicommerceops.api_dependencies import get_db
from omnicommerceops.api_routes import get_clock


@pytest.fixture
def client(retail_session):
    app.dependency_overrides[get_db] = lambda: retail_session
    app.dependency_overrides[get_clock] = lambda: datetime(2026, 1, 14, 18, tzinfo=timezone.utc)
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_list_and_detail_hide_selected_scenario(client):
    cases = client.get("/rounds/1/cases")
    assert cases.status_code == 200
    assert len(cases.json()) == 3
    assert "selected_for_run" not in str(cases.json())
    assert all(case["sales_outcome"] is None for case in cases.json())
    detail = client.get(f"/cases/{cases.json()[0]['id']}")
    assert detail.status_code == 200
    assert "selected_for_run" not in str(detail.json())


def test_plan_run_and_duplicate_conflict(client):
    cases = client.get("/rounds/1/cases").json()
    for case in cases:
        response = client.post(f"/cases/{case['id']}/demand-plan", json={
            "forecast_volume_units": 60,
            "chosen_order_units": 0,
            "reason": "Exercise baseline",
            "planner_identifier": "demand_planner",
        })
        assert response.status_code == 200
        assert response.json()["forecast_volume_units"] == 60
    run = client.post("/rounds/1/run")
    assert run.status_code == 200
    assert len(run.json()["outcomes"]) == 3
    duplicate = client.post("/rounds/1/run")
    assert duplicate.status_code == 409
    assert duplicate.json()["code"] == "ROUND_ALREADY_RUN"


def test_missing_and_invalid_commands(client):
    assert client.get("/cases/99999").status_code == 404
    assert client.get("/rounds/3/cases").status_code == 404
    case_id = client.get("/rounds/1/cases").json()[0]["id"]
    assert client.post(f"/cases/{case_id}/demand-plan", json={
        "forecast_volume_units": -1, "chosen_order_units": 0,
        "reason": "Bad", "planner_identifier": "demand_planner",
    }).status_code == 422
    assert client.post(f"/cases/{case_id}/campaign-decision", json={
        "decision": "REPEAT", "reason": "Too early",
        "category_manager_identifier": "category_manager",
    }).status_code == 409


@pytest.mark.parametrize("extra", ["selected_for_run", "sales_volume_units", "net_contribution_usd", "analysis_metrics"])
def test_server_owned_fields_rejected(client, extra):
    case_id = client.get("/rounds/1/cases").json()[0]["id"]
    payload = {"forecast_volume_units": 60, "chosen_order_units": 0,
               "reason": "Exercise", "planner_identifier": "demand_planner", extra: 1}
    assert client.post(f"/cases/{case_id}/demand-plan", json=payload).status_code == 422


def test_alpha_routes_are_not_public(client):
    assert client.post("/storefront/checkout-order", json={}).status_code == 404
    assert client.post("/inventory/restock-units", json={}).status_code == 404
    assert client.get("/analytics/sales-summary").status_code == 404


def test_planner_can_preview_server_order_suggestion_before_saving(client):
    cola = next(case for case in client.get("/rounds/1/cases").json()
                if case["product_key"] == "PROD_COLA")
    response = client.get(f"/cases/{cola['id']}", params={"forecast_volume_units": 90})
    assert response.status_code == 200
    assert response.json()["suggested_order_units"] == 10  # 90 + 20 safety - 100 stock
    assert response.json()["forecast_volume_units"] is None  # preview did not save a plan
    assert client.get(f"/cases/{cola['id']}", params={
        "forecast_volume_units": -1,
    }).status_code == 422


def _run_round(client, number):
    for case in client.get(f"/rounds/{number}/cases").json():
        assert client.post(f"/cases/{case['id']}/demand-plan", json={
            "forecast_volume_units": 60, "chosen_order_units": 0,
            "reason": "Analysis exercise", "planner_identifier": "demand_planner",
        }).status_code == 200
    assert client.post(f"/rounds/{number}/run").status_code == 200


def test_case_metrics_appear_only_after_sales(client):
    cases = client.get("/rounds/1/cases").json()
    assert all(case["analysis_metrics"] is None for case in cases)
    assert "selected_for_run" not in str(cases)
    _run_round(client, 1)
    cola = client.get(f"/cases/{cases[0]['id']}").json()
    assert cola["analysis_metrics"] == {
        "gross_profit_usd": "400.00", "revenue_growth_percentage": None,
        "sales_volume_growth_percentage": None, "average_selling_price_usd": "9.00",
        "gross_margin_percentage": "55.56", "demand_fill_rate_percentage": "100.00",
        "absolute_forecast_error_percentage": "33.33", "incremental_promotion_roi_percentage": "100.00",
    }


def test_round_two_metrics_match_previous_product_and_region(client, retail_session):
    from datetime import date
    from omnicommerceops.database_models import DemandScenario, RegionalStock, RoundCase, SalesOutcome
    _run_round(client, 1)
    _run_round(client, 2)
    retail_session.add(RegionalStock(product_key="PROD_COLA", operating_region="SOUTH",
                                    current_stock_units=500, safety_stock_units=20, supplier_lead_days=2))
    for number, sold in ((1, 10), (2, 20)):
        case = RoundCase(product_key="PROD_COLA", operating_region="SOUTH", round_number=number,
                         planning_date=date(2026, 1, 1), selling_period_end_date=date(2026, 1, 14),
                         forecast_volume_units=60, chosen_order_units=0)
        retail_session.add(case)
        retail_session.flush()
        retail_session.add(DemandScenario(round_case_id=case.id, demand_level="MEDIUM",
                                         base_demand_units=sold, campaign_demand_change_units=0,
                                         selected_for_run=True))
        retail_session.add(SalesOutcome(
            round_case_id=case.id, selected_demand_level="MEDIUM", customer_demand_units=sold,
            sales_volume_units=sold, lost_sales_units=0, selling_unit_retail_price=10,
            gross_sales_revenue=sold * 10, stock_before_units=500, stock_after_units=500-sold,
            run_timestamp=datetime(2026, 1, 14, tzinfo=timezone.utc),
        ))
    retail_session.commit()
    cases = client.get("/rounds/2/cases").json()
    north = next(c for c in cases if c["product_key"] == "PROD_COLA" and c["operating_region"] == "NORTH")
    south = next(c for c in cases if c["product_key"] == "PROD_COLA" and c["operating_region"] == "SOUTH")
    assert north["analysis_metrics"]["revenue_growth_percentage"] == "-72.22"
    assert north["analysis_metrics"]["sales_volume_growth_percentage"] == "-75.00"
    assert south["analysis_metrics"]["revenue_growth_percentage"] == "100.00"
    assert south["analysis_metrics"]["sales_volume_growth_percentage"] == "100.00"


def test_case_metrics_ignore_preview_forecast(client):
    _run_round(client, 1)
    cola = client.get("/rounds/1/cases").json()[0]
    preview = client.get(f"/cases/{cola['id']}", params={"forecast_volume_units": 999}).json()
    assert preview["analysis_metrics"]["absolute_forecast_error_percentage"] == "33.33"
    assert preview["forecast_error_percentage"] == "33.33"
    assert preview["forecast_volume_units"] == 60


def test_analysis_reads_do_not_change_business_state(client, retail_session):
    from sqlalchemy import select
    from sqlmodel import SQLModel
    _run_round(client, 1)
    def snapshot():
        return [retail_session.execute(select(table)).all() for table in SQLModel.metadata.sorted_tables]
    before = snapshot()
    for number in (1, 2):
        for case in client.get(f"/rounds/{number}/cases").json():
            assert "analysis_metrics" in client.get(f"/cases/{case['id']}").json()
    assert snapshot() == before
