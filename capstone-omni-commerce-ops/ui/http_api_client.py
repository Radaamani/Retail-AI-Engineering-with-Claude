"""The dashboard reads and changes RetailOps only through HTTP."""

import requests


class RetailApiClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip("/")

    def _request(self, method: str, path: str, payload: dict | None = None,
                 params: dict | None = None):
        response = requests.request(method, f"{self.base_url}{path}", json=payload,
                                    params=params, timeout=10)
        response.raise_for_status()
        return response.json()

    def list_round_cases(self, round_number: int) -> list[dict]:
        return self._request("GET", f"/rounds/{round_number}/cases")

    def get_case(self, case_id: int, forecast_volume_units: int | None = None) -> dict:
        params = None if forecast_volume_units is None else {
            "forecast_volume_units": forecast_volume_units,
        }
        return self._request("GET", f"/cases/{case_id}", params=params)

    def record_demand_plan(self, case_id: int, forecast_volume_units: int,
                           chosen_order_units: int, reason: str) -> dict:
        return self._request("POST", f"/cases/{case_id}/demand-plan", {
            "forecast_volume_units": forecast_volume_units, "chosen_order_units": chosen_order_units,
            "reason": reason, "planner_identifier": "demand_planner",
        })

    def plan_campaign(self, case_id: int, campaign_unit_retail_price: str,
                      marketing_promotion_spend: str, reason: str) -> dict:
        return self._request("PUT", f"/cases/{case_id}/campaign", {
            "campaign_unit_retail_price": campaign_unit_retail_price,
            "marketing_promotion_spend": marketing_promotion_spend, "reason": reason,
            "category_manager_identifier": "category_manager",
        })

    def receive_supply_order(self, order_id: int, received_date: str) -> dict:
        return self._request("POST", f"/supply-orders/{order_id}/receipt", {
            "received_date": received_date, "planner_identifier": "demand_planner",
        })

    def run_sales_period(self, round_number: int) -> dict:
        return self._request("POST", f"/rounds/{round_number}/run")

    def record_campaign_decision(self, case_id: int, decision: str, reason: str) -> dict:
        return self._request("POST", f"/cases/{case_id}/campaign-decision", {
            "decision": decision, "reason": reason,
            "category_manager_identifier": "category_manager",
        })
