from __future__ import annotations

import pandas as pd
import streamlit as st

from agent.router import route_query
from agent.prompts import (
    format_item_details,
    format_portfolio_summary,
    format_store_summary,
    format_table_result,
    get_item_manager_interpretation,
    get_portfolio_manager_interpretation,
    get_store_manager_interpretation,
    get_table_manager_interpretation,
)


st.set_page_config(
    page_title="Agentic Inventory Planning Assistant",
    layout="wide",
)

st.title("Agentic Inventory Planning Assistant")
st.caption(
    "A beginner-friendly agentic AI project that routes business questions to data tools over forecast outputs."
)

st.markdown(
    """
**Examples of questions you can ask**
- Which items are highest risk this week?
- Show top replenishment priorities.
- Summarize the portfolio.
- What is happening in store S001?
- Explain S001 P0004.
"""
)


def render_response(route_result: dict) -> str:
    route = route_result.get("route")
    result = route_result.get("result")
    note = route_result.get("note")

    if route == "portfolio_summary":
        response = format_portfolio_summary(result)
    elif route == "store_summary":
        response = format_store_summary(result)
    elif route == "item_details":
        response = format_item_details(result)
    elif route == "top_high_risk_items":
        response = format_table_result("Top High-Risk Items", result)
    elif route == "top_replenishment_priorities":
        response = format_table_result("Top Replenishment Priorities", result)
    else:
        response = str(result)

    if note:
        response += f"\n\nNote: {note}"

    return response


def render_manager_interpretation(route_result: dict) -> str | None:
    route = route_result.get("route")
    result = route_result.get("result")

    if route == "portfolio_summary":
        return get_portfolio_manager_interpretation(result)
    if route == "store_summary":
        return get_store_manager_interpretation(result)
    if route == "item_details":
        return get_item_manager_interpretation(result)
    if route == "top_high_risk_items":
        return get_table_manager_interpretation("Top High-Risk Items", result)
    if route == "top_replenishment_priorities":
        return get_table_manager_interpretation("Top Replenishment Priorities", result)

    return None


def maybe_render_table(route_result: dict) -> None:
    route = route_result.get("route")
    result = route_result.get("result")

    if route in ["top_high_risk_items", "top_replenishment_priorities"] and isinstance(result, list):
        if result:
            st.markdown("### Structured View")
            st.dataframe(pd.DataFrame(result), use_container_width=True, hide_index=True)


def render_suggested_follow_ups(route_result: dict) -> None:
    follow_ups = route_result.get("suggested_follow_ups", [])
    if follow_ups:
        st.markdown("### Suggested Next Questions")
        for suggestion in follow_ups:
            st.markdown(f"- {suggestion}")


def get_compact_summary(route_result: dict) -> str:
    route = route_result.get("route")
    result = route_result.get("result")

    if route == "portfolio_summary":
        return (
            f"Portfolio summary: {result['high_risk_items']} high-risk items, "
            f"{result['medium_risk_items']} medium-risk items, "
            f"total recommended order qty {result['total_recommended_order_qty']}."
        )

    if route == "store_summary":
        if "error" in result:
            return result["error"]
        return (
            f"Store {result['store_id']}: {result['high_risk_items']} high-risk items, "
            f"{result['medium_risk_items']} medium-risk items, "
            f"total recommended order qty {result['total_recommended_order_qty']}."
        )

    if route == "item_details":
        if "error" in result:
            return result["error"]
        return (
            f"Item {result['store_id']} - {result['product_id']}: "
            f"risk {result['stockout_risk']}, recommended order qty {result['recommended_order_qty']}."
        )

    if route in ["top_high_risk_items", "top_replenishment_priorities"]:
        if isinstance(result, list) and result:
            top = result[0]
            return (
                f"Top result: Store {top['store_id']} / Product {top['product_id']} | "
                f"recommended qty {top['recommended_order_qty']} | risk {top['stockout_risk']}."
            )
        return "No records found."

    return "Assistant completed a routing and analysis step."


def render_assistant_full(route_result: dict) -> None:
    response_text = render_response(route_result)
    manager_text = render_manager_interpretation(route_result)
    reasoning = route_result.get("reasoning")

    st.markdown("### Assistant Response")

    if reasoning:
        st.info(f"Agent reasoning: {reasoning}")

    st.markdown(f"```text\n{response_text}\n```")

    if manager_text:
        st.markdown("### Manager Recommendation")
        st.success(manager_text)

    maybe_render_table(route_result)
    render_suggested_follow_ups(route_result)

    with st.expander("Routing Details"):
        st.json(route_result)


def render_assistant_compact(route_result: dict, turn_number: int) -> None:
    compact_summary = get_compact_summary(route_result)
    reasoning = route_result.get("reasoning")
    manager_text = render_manager_interpretation(route_result)
    response_text = render_response(route_result)

    st.markdown(f"**Previous Assistant Turn {turn_number}**")
    st.markdown(compact_summary)

    with st.expander("Expand previous turn"):
        if reasoning:
            st.info(f"Agent reasoning: {reasoning}")

        st.markdown(f"```text\n{response_text}\n```")

        if manager_text:
            st.markdown("### Manager Recommendation")
            st.success(manager_text)

        maybe_render_table(route_result)

        st.markdown("### Routing Details")
        st.json(route_result)


if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


total_messages = len(st.session_state.chat_history)
last_assistant_index = None
for idx, message in enumerate(st.session_state.chat_history):
    if message["role"] == "assistant":
        last_assistant_index = idx

assistant_turn_counter = 0

for idx, message in enumerate(st.session_state.chat_history):
    role = message["role"]

    if role == "user":
        with st.chat_message("user"):
            st.markdown(message["content"])
    elif role == "assistant":
        assistant_turn_counter += 1
        with st.chat_message("assistant"):
            if idx == last_assistant_index:
                render_assistant_full(message["route_result"])
            else:
                render_assistant_compact(message["route_result"], assistant_turn_counter)


user_query = st.chat_input("Ask a planning question")

if user_query:
    st.session_state.chat_history.append(
        {
            "role": "user",
            "content": user_query,
        }
    )

    with st.chat_message("user"):
        st.markdown(user_query)

    try:
        route_result = route_query(user_query)

        st.session_state.chat_history.append(
            {
                "role": "assistant",
                "route_result": route_result,
            }
        )

        with st.chat_message("assistant"):
            render_assistant_full(route_result)

    except Exception as e:
        st.error(f"Something went wrong: {e}")


st.markdown("---")
if st.button("Clear Chat History"):
    st.session_state.chat_history = []
    st.rerun()