"""One RetailOps product, two business-user work areas, two sales periods."""

import os
import sys
from pathlib import Path

import requests
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ui.http_api_client import RetailApiClient
from ui.analysis_view import render_analysis
from ui.planning_view import render_planning
from ui.promotion_view import render_promotions

st.set_page_config(page_title="RetailOps", page_icon="🛒", layout="wide")


@st.cache_resource
def get_client() -> RetailApiClient:
    return RetailApiClient(os.environ.get("RETAILOPS_API_URL", "http://localhost:8000"))


def main() -> None:
    st.title("RetailOps")
    st.caption("Plan demand, run a sales period, and review campaign performance.")
    client = get_client()
    try:
        first_round = client.list_round_cases(1)
        first_complete = all(case["sales_outcome"] is not None for case in first_round)
        selected_round = st.selectbox("Sales period", [1, 2], index=0,
                                      format_func=lambda number: f"Round {number}")
        cases = client.list_round_cases(selected_round)
        if selected_round == 2 and not first_complete:
            st.info("Complete round 1 before working on round 2.")
            return
        ready = all(case["forecast_volume_units"] is not None for case in cases)
        already_run = all(case["sales_outcome"] is not None for case in cases)
        if already_run:
            st.success("This sales period has run. Actual demand and stock are now visible.")
        else:
            st.caption("Running sales reveals the preset demand scenario and posts stock changes for all cases together.")
            if st.button("Run sales period", disabled=not ready):
                client.run_sales_period(selected_round)
                st.rerun()
            if not ready:
                st.info("Record a demand plan for every case to enable the sales run.")
        planning, promotions = st.tabs(["Demand Planning", "Promotion Performance"])
        with planning:
            render_planning(client, cases)
        with promotions:
            render_promotions(client, cases)
        export_cases = first_round if selected_round == 1 else first_round + cases
        render_analysis(cases, export_cases, selected_round)
    except requests.HTTPError as error:
        try:
            body = error.response.json()
            st.error(f"{body['message']} ({body['code']})")
        except (ValueError, KeyError):
            st.error(str(error))
    except requests.ConnectionError:
        st.error("RetailOps API is unavailable. Start the API and refresh this page.")


if __name__ == "__main__":
    main()
