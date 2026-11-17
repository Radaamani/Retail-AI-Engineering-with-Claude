"""Category-manager work area: planned campaign versus no-campaign result."""

import streamlit as st


def render_promotions(client, cases: list[dict]) -> None:
    st.subheader("Promotion Performance")
    st.caption("Working as seeded category_manager. The selected demand level stays hidden until sales run.")
    for case in cases:
        with st.expander(f"{case['product_name']} · {case['operating_region']}", expanded=True):
            st.write(f"Demand scenario range: {case['demand_range_low_units']}–{case['demand_range_high_units']} units")
            st.write(f"Regular price: ${case['regular_unit_retail_price']} per unit · Unit cost: ${case['unit_wholesale_cost']}")
            campaign = case["campaign"]
            if "plan_campaign" in case["permitted_actions"]:
                with st.form(f"campaign_{case['id']}"):
                    price = st.number_input("Campaign price ($/unit)", min_value=0.01,
                                            value=float(campaign["campaign_unit_retail_price"] if campaign else case["regular_unit_retail_price"]),
                                            key=f"campaign_price_{case['id']}")
                    spend = st.number_input("Promotion spend ($)", min_value=0.0,
                                            value=float(campaign["marketing_promotion_spend"] if campaign else 0),
                                            key=f"campaign_spend_{case['id']}")
                    reason = st.text_input("Campaign reason", value=campaign["plan_reason"] if campaign else "",
                                           key=f"campaign_reason_{case['id']}")
                    if st.form_submit_button("Save campaign plan"):
                        client.plan_campaign(case["id"], f"{price:.2f}", f"{spend:.2f}", reason)
                        st.rerun()
            elif campaign:
                st.write(f"Campaign price: ${campaign['campaign_unit_retail_price']} · Spend: ${campaign['marketing_promotion_spend']}")
            outcome = case["sales_outcome"]
            assessment = case["campaign_assessment"]
            if outcome:
                st.write(f"Revealed demand: {outcome['selected_demand_level']} · Actual demand: {outcome['customer_demand_units']} units")
            if assessment:
                st.write(f"Actual gross profit: ${assessment['actual_gross_profit_usd']} · Without campaign: ${assessment['comparison_gross_profit_usd']}")
                st.metric("Estimated net contribution", f"${assessment['net_contribution_usd']}")
                if assessment["stock_constrained"]:
                    st.warning("Stock constrained: the campaign comparison may understate demand impact.")
                if "record_campaign_decision" in case["permitted_actions"]:
                    with st.form(f"decision_{case['id']}"):
                        decision = st.selectbox("Next decision", ["REPEAT", "ADJUST", "STOP"], key=f"decision_{case['id']}")
                        reason = st.text_input("Decision reason", key=f"decision_reason_{case['id']}")
                        if st.form_submit_button("Record campaign decision"):
                            client.record_campaign_decision(case["id"], decision, reason)
                            st.rerun()
                elif campaign["decision"]:
                    st.success(f"Decision: {campaign['decision']} · {campaign['decision_reason']}")
