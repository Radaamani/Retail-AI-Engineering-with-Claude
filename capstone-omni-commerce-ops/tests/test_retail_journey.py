"""A business user can complete two periods through HTTP alone."""

from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlmodel import select

from omnicommerceops.api_app import app
from omnicommerceops.api_dependencies import get_db
from omnicommerceops.api_routes import get_clock
from omnicommerceops.database_models import RegionalStock, SalesOutcome


@pytest.fixture
def client(retail_session):
    app.dependency_overrides[get_db] = lambda: retail_session
    app.dependency_overrides[get_clock] = lambda: datetime(2026, 1, 14, 18, tzinfo=timezone.utc)
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_two_round_journey(client, retail_session):
    first = client.get("/rounds/1/cases").json()
    cola = next(case for case in first if case["product_key"] == "PROD_COLA")
    assert client.put(f"/cases/{cola['id']}/campaign", json={
        "campaign_unit_retail_price": "9.00", "marketing_promotion_spend": "20.00",
        "reason": "Test incremental demand", "category_manager_identifier": "category_manager",
    }).status_code == 200
    for case in first:
        response = client.post(f"/cases/{case['id']}/demand-plan", json={
            "forecast_volume_units": 60, "chosen_order_units": 20 if case == cola else 0,
            "reason": "Baseline exercise", "planner_identifier": "demand_planner",
        })
        assert response.status_code == 200
    order_id = client.get(f"/cases/{cola['id']}").json()["supply_order"]["id"]
    assert client.post(f"/supply-orders/{order_id}/receipt", json={
        "received_date": "2026-01-03", "planner_identifier": "demand_planner",
    }).status_code == 200
    first_run = client.post("/rounds/1/run")
    assert first_run.status_code == 200
    assert len(first_run.json()["outcomes"]) == 3
    assert client.post(f"/cases/{cola['id']}/campaign-decision", json={
        "decision": "REPEAT", "reason": "Positive estimated contribution",
        "category_manager_identifier": "category_manager",
    }).status_code == 200
    second = client.get("/rounds/2/cases").json()
    assert next(case for case in second if case["product_key"] == "PROD_COLA")["current_stock_units"] == 40
    for case in second:
        assert client.post(f"/cases/{case['id']}/demand-plan", json={
            "forecast_volume_units": 70, "chosen_order_units": 0,
            "reason": "Use round-one actuals", "planner_identifier": "demand_planner",
        }).status_code == 200
    second_run = client.post("/rounds/2/run")
    assert second_run.status_code == 200
    assert len(second_run.json()["outcomes"]) == 3
    assert len(retail_session.exec(select(SalesOutcome)).all()) == 6
    assert all(stock.current_stock_units >= 0 for stock in retail_session.exec(select(RegionalStock)).all())
    assert client.get(f"/cases/{cola['id']}").json()["current_stock_units"] == client.get(
        f"/cases/{next(case for case in second if case['product_key'] == 'PROD_COLA')['id']}"
    ).json()["current_stock_units"]


def test_ui_client_maps_paths(monkeypatch):
    from ui.http_api_client import RetailApiClient
    calls = []

    class Response:
        def raise_for_status(self):
            pass

        def json(self):
            return {"ok": True}

    def fake_request(method, url, **kwargs):
        calls.append((method, url, kwargs))
        return Response()

    monkeypatch.setattr("requests.request", fake_request)
    api = RetailApiClient("http://example.test")
    api.list_round_cases(1)
    api.get_case(2)
    api.get_case(2, 90)
    api.record_demand_plan(2, 60, 0, "Baseline")
    api.plan_campaign(2, "9.00", "20.00", "Test")
    api.receive_supply_order(3, "2026-01-03")
    api.run_sales_period(1)
    api.record_campaign_decision(2, "REPEAT", "Good")
    assert [(method, url.split(".test")[-1]) for method, url, _ in calls] == [
        ("GET", "/rounds/1/cases"), ("GET", "/cases/2"), ("GET", "/cases/2"),
        ("POST", "/cases/2/demand-plan"), ("PUT", "/cases/2/campaign"),
        ("POST", "/supply-orders/3/receipt"), ("POST", "/rounds/1/run"),
        ("POST", "/cases/2/campaign-decision"),
    ]
    assert calls[2][2]["params"] == {"forecast_volume_units": 90}


def test_dashboard_does_not_import_alpha_tabs():
    from pathlib import Path
    source = (Path(__file__).parents[1] / "ui" / "retail_dashboard.py").read_text()
    assert "storefront_tab" not in source
    assert "operations_tab" not in source


def test_planning_screen_previews_server_suggestion_before_save(client, monkeypatch):
    from pathlib import Path
    from streamlit.testing.v1 import AppTest
    from ui.http_api_client import RetailApiClient

    def in_process_request(self, method, path, payload=None, params=None):
        response = client.request(method, path, json=payload, params=params)
        response.raise_for_status()
        return response.json()

    monkeypatch.setattr(RetailApiClient, "_request", in_process_request)
    dashboard = AppTest.from_file(str(Path(__file__).parents[1] / "ui" / "retail_dashboard.py")).run()
    assert not dashboard.exception
    assert any("Suggested order: 0 units" in item.value for item in dashboard.caption)
    dashboard.number_input[0].set_value(90).run()
    assert not dashboard.exception
    assert any("Suggested order: 10 units" in item.value for item in dashboard.caption)
