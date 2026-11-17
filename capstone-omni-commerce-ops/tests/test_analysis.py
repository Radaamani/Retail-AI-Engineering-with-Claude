"""Students can inspect and export recorded outcomes without changing the exercise."""

import csv
from datetime import datetime, timezone
from decimal import Decimal
from io import StringIO
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from omnicommerceops.api_app import app
from omnicommerceops.api_dependencies import get_db
from omnicommerceops.api_routes import get_clock


@pytest.fixture
def client(retail_session):
    app.dependency_overrides[get_db] = lambda: retail_session
    app.dependency_overrides[get_clock] = lambda: datetime(2026, 1, 14, 18, tzinfo=timezone.utc)
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()


def _run_round(client, number):
    for case in client.get(f"/rounds/{number}/cases").json():
        assert client.post(f"/cases/{case['id']}/demand-plan", json={
            "forecast_volume_units": 60, "chosen_order_units": 0,
            "reason": "Analysis exercise", "planner_identifier": "demand_planner",
        }).status_code == 200
    assert client.post(f"/rounds/{number}/run").status_code == 200


def _csv_rows(cases):
    from ui.analysis_view import analysis_csv
    return list(csv.DictReader(StringIO(analysis_csv(cases))))


def test_analysis_csv_exports_only_completed_public_results(client):
    from ui.analysis_view import analysis_csv, analysis_rows
    assert _csv_rows(client.get("/rounds/1/cases").json()) == []
    _run_round(client, 1)
    first = client.get("/rounds/1/cases").json()
    second = client.get("/rounds/2/cases").json()
    rows = _csv_rows(list(reversed(first)) + second)
    assert [row["product_key"] for row in rows] == ["PROD_CHIPS", "PROD_COLA", "PROD_OJ"]
    assert [row["round_number"] for row in rows] == ["1", "1", "1"]
    assert len(analysis_rows(first + second)) == 3
    reader = csv.DictReader(StringIO(analysis_csv(first)))
    assert reader.fieldnames == (
        "round_number case_id product_key product_name operating_region forecast_volume_units "
        "chosen_order_units safety_stock_units supplier_lead_days customer_demand_units "
        "sales_volume_units lost_sales_units stock_before_units stock_after_units "
        "selling_unit_retail_price unit_wholesale_cost gross_sales_revenue marketing_promotion_spend "
        "comparison_gross_profit_usd net_contribution_usd stock_constrained gross_profit_usd "
        "revenue_growth_percentage sales_volume_growth_percentage average_selling_price_usd "
        "gross_margin_percentage demand_fill_rate_percentage absolute_forecast_error_percentage "
        "incremental_promotion_roi_percentage"
    ).split()


def test_analysis_csv_preserves_missing_zero_and_quoted_values(client):
    _run_round(client, 1)
    cases = client.get("/rounds/1/cases").json()
    cases[0]["product_name"] = 'Cola, "family size"'
    rows = {row["product_key"]: row for row in _csv_rows(cases)}
    assert rows["PROD_COLA"]["product_name"] == 'Cola, "family size"'
    assert rows["PROD_COLA"]["stock_constrained"] == "False"
    assert rows["PROD_COLA"]["revenue_growth_percentage"] == ""
    assert rows["PROD_CHIPS"]["stock_after_units"] == "0"
    assert Decimal(rows["PROD_CHIPS"]["marketing_promotion_spend"]) == 0
    assert rows["PROD_CHIPS"]["incremental_promotion_roi_percentage"] == ""
    assert rows["PROD_CHIPS"]["comparison_gross_profit_usd"] == ""


def test_analysis_export_uses_recorded_stock_after_later_round(client):
    _run_round(client, 1)
    first = client.get("/rounds/1/cases").json()
    before = _csv_rows(first)
    _run_round(client, 2)
    cases = client.get("/rounds/2/cases").json() + client.get("/rounds/1/cases").json()
    rows = _csv_rows(cases)
    assert rows[:3] == before
    assert len(rows) == 6
    cola = next(row for row in rows if row["product_key"] == "PROD_COLA" and row["round_number"] == "1")
    assert (cola["stock_before_units"], cola["stock_after_units"]) == ("100", "20")
    assert "current_stock_units" not in cola
    assert "selected_demand_level" not in cola
    assert "selected_for_run" not in cola


def test_analysis_export_retains_campaign_context(client):
    cola = client.get("/rounds/1/cases").json()[0]
    assert client.put(f"/cases/{cola['id']}/campaign", json={
        "campaign_unit_retail_price": "9", "marketing_promotion_spend": "0",
        "reason": "Zero spend example", "category_manager_identifier": "category_manager",
    }).status_code == 200
    _run_round(client, 1)
    rows = {row["product_key"]: row for row in _csv_rows(client.get("/rounds/1/cases").json())}
    assert Decimal(rows["PROD_COLA"]["net_contribution_usd"]) == 40
    assert rows["PROD_COLA"]["incremental_promotion_roi_percentage"] == ""
    assert Decimal(rows["PROD_OJ"]["net_contribution_usd"]) == -60
    assert Decimal(rows["PROD_OJ"]["incremental_promotion_roi_percentage"]) == -150
    assert rows["PROD_CHIPS"]["net_contribution_usd"] == ""
    _run_round(client, 2)
    chips = next(row for row in _csv_rows(client.get("/rounds/2/cases").json()) if row["product_key"] == "PROD_CHIPS")
    assert chips["stock_constrained"] == "True"
    assert Decimal(chips["incremental_promotion_roi_percentage"]) == -100
    assert chips["demand_fill_rate_percentage"] == "0.00"


def test_analysis_section_tracks_selected_round_and_download(client, monkeypatch):
    import streamlit as st
    from streamlit.testing.v1 import AppTest
    from ui.http_api_client import RetailApiClient

    def in_process_request(self, method, path, payload=None, params=None):
        response = client.request(method, path, json=payload, params=params)
        response.raise_for_status()
        return response.json()

    # Keep the real widget; capture its payload because AppTest does not expose download bytes.
    downloads = []
    real_download = st.download_button

    def capture_download(label, data, **kwargs):
        downloads.append({"label": label, "data": data, **kwargs})
        return real_download(label, data, **kwargs)

    monkeypatch.setattr(RetailApiClient, "_request", in_process_request)
    monkeypatch.setattr(st, "download_button", capture_download)
    dashboard = AppTest.from_file(str(Path(__file__).parents[1] / "ui/retail_dashboard.py")).run()
    assert not dashboard.exception
    assert downloads and downloads[-1]["disabled"] is True
    assert any("Run this sales period" in item.value for item in dashboard.info)
    _run_round(client, 1)
    dashboard.run()
    assert not dashboard.exception
    assert len(dashboard.dataframe[0].value) == 3
    assert dashboard.dataframe[0].value.iloc[0]["Revenue growth %"] == "N/A"
    download = downloads[-1]
    assert download["label"] == "Download analysis CSV"
    assert download["mime"] == "text/csv"
    assert download["file_name"] == "retailops_analysis_through_round_1.csv"
    assert download["disabled"] is False
    assert len(list(csv.DictReader(StringIO(download["data"])))) == 3
    dashboard.selectbox[0].set_value(2).run()
    assert not dashboard.exception
    assert len(dashboard.dataframe) == 0
    assert any("Run this sales period" in item.value for item in dashboard.info)
    assert len(list(csv.DictReader(StringIO(downloads[-1]["data"])))) == 3
    _run_round(client, 2)
    dashboard.run()
    assert not dashboard.exception
    assert len(dashboard.dataframe[0].value) == 3
    assert downloads[-1]["file_name"] == "retailops_analysis_through_round_2.csv"
    rows = list(csv.DictReader(StringIO(downloads[-1]["data"])))
    assert len(rows) == 6
    assert {row["round_number"] for row in rows} == {"1", "2"}
    cola = next(row for row in rows if row["product_key"] == "PROD_COLA" and row["round_number"] == "2")
    assert Decimal(cola["revenue_growth_percentage"]) == Decimal("-72.22")
