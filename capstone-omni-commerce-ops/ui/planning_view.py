"""Demand-planner work area: forecast, order, receipt, and actuals."""

from datetime import date

import streamlit as st


def render_planning(client, cases: list[dict]) -> None:
    st.subheader("Demand Planning")
    st.caption("Working as seeded demand_planner. Ordered stock becomes sellable only after receipt.")
    for case in cases:
        with st.expander(f"{case['product_name']} · {case['operating_region']}", expanded=True):
            st.write(f"Stock: {case['current_stock_units']} units · Safety stock: {case['safety_stock_units']} units")
            st.write(f"Supplier lead time: {case['supplier_lead_days']} days · Demand range: {case['demand_range_low_units']}–{case['demand_range_high_units']} units")
            if case["warning"]:
                st.warning(case["warning"])
            if "record_demand_plan" in case["permitted_actions"]:
                forecast = st.number_input(
                    "Forecast demand (units)", min_value=0,
                    value=case["demand_range_low_units"], key=f"forecast_{case['id']}",
                )
                preview = client.get_case(case["id"], forecast)
                suggested = preview["suggested_order_units"]
                st.caption(f"Suggested order: {suggested} units (server calculation).")
                with st.form(f"plan_{case['id']}"):
                    ordered = st.number_input(
                        "Chosen order (units)", min_value=0, value=suggested,
                        key=f"order_{case['id']}_{forecast}",
                    )
                    reason = st.text_input("Planning reason", key=f"plan_reason_{case['id']}")
                    if st.form_submit_button("Save demand plan"):
                        client.record_demand_plan(case["id"], forecast, ordered, reason)
                        st.rerun()
            elif case["forecast_volume_units"] is not None:
                st.write(f"Forecast: {case['forecast_volume_units']} units · Chosen order: {case['chosen_order_units']} units")
                st.write(f"Server suggestion at current stock: {case['suggested_order_units']} units")
                st.caption(f"Reason: {case['plan_reason']}")
            order = case["supply_order"]
            if order:
                st.write(f"Supply order: {order['ordered_units']} units · Due: {order['due_date']}")
                if "receive_supply_order" in case["permitted_actions"]:
                    received = st.date_input("Receipt date", value=date.fromisoformat(order["due_date"]), key=f"receipt_{case['id']}")
                    if st.button("Record stock receipt", key=f"receive_{case['id']}"):
                        client.receive_supply_order(order["id"], received.isoformat())
                        st.rerun()
                elif order["received_date"]:
                    st.success(f"Received {order['received_date']}")
            outcome = case["sales_outcome"]
            if outcome:
                st.write(f"Actual demand: {outcome['customer_demand_units']} units · Sold: {outcome['sales_volume_units']} units · Lost sales: {outcome['lost_sales_units']} units")
                st.write(f"Forecast error: {case['forecast_error_units']} units ({case['forecast_error_percentage']}%)")
                st.write(f"Stock after sales: {outcome['stock_after_units']} units")
