from __future__ import annotations

import re
from agent.tools import (
    get_item_details,
    get_store_summary,
    get_top_high_risk_items,
    get_top_replenishment_priorities,
    summarize_portfolio,
)


def extract_store_id(text: str) -> str | None:
    match = re.search(r"\bS\d{3}\b", text.upper())
    return match.group(0) if match else None


def extract_product_id(text: str) -> str | None:
    match = re.search(r"\bP\d{4}\b", text.upper())
    return match.group(0) if match else None


def detect_intent(query: str, store_id: str | None, product_id: str | None) -> dict:
    """
    Lightweight planning layer for the assistant.
    It decides the likely user intent before selecting a tool.
    """
    q = query.lower().strip()

    if store_id and product_id:
        return {
            "intent": "item_details",
            "reasoning": "The user mentioned both a store ID and a product ID, so the assistant should inspect that specific item.",
        }

    if store_id:
        return {
            "intent": "store_summary",
            "reasoning": "The user mentioned a store ID, so the assistant should summarize that store's planning situation.",
        }

    if any(phrase in q for phrase in ["high risk", "highest risk", "stockout risk", "risky items"]):
        return {
            "intent": "top_high_risk_items",
            "reasoning": "The user is asking about risk concentration, so the assistant should retrieve the top high-risk items.",
        }

    if any(phrase in q for phrase in ["replenishment", "priority", "recommended order", "top items"]):
        return {
            "intent": "top_replenishment_priorities",
            "reasoning": "The user is asking about replenishment action, so the assistant should retrieve the top replenishment priorities.",
        }

    if any(phrase in q for phrase in ["portfolio", "summary", "overall", "overview", "all items"]):
        return {
            "intent": "portfolio_summary",
            "reasoning": "The user is asking for a broad overview, so the assistant should summarize the full portfolio.",
        }

    return {
        "intent": "portfolio_summary",
        "reasoning": "No exact intent match was found, so the assistant will fall back to an overall portfolio summary.",
    }


def execute_intent(intent: str, store_id: str | None, product_id: str | None):
    """Run the appropriate tool for the chosen intent."""
    if intent == "item_details":
        return get_item_details(store_id, product_id)

    if intent == "store_summary":
        return get_store_summary(store_id)

    if intent == "top_high_risk_items":
        return get_top_high_risk_items().to_dict(orient="records")

    if intent == "top_replenishment_priorities":
        return get_top_replenishment_priorities().to_dict(orient="records")

    return summarize_portfolio()


def get_suggested_follow_ups(intent: str, store_id: str | None, product_id: str | None) -> list[str]:
    """Return suggested next questions based on the current route."""
    if intent == "portfolio_summary":
        return [
            "Which items are highest risk this week?",
            "Show top replenishment priorities.",
            "What is happening in store S005?",
        ]

    if intent == "top_high_risk_items":
        return [
            "Show top replenishment priorities.",
            "Summarize the portfolio.",
            "What is happening in store S005?",
        ]

    if intent == "top_replenishment_priorities":
        return [
            "Which items are highest risk this week?",
            "Summarize the portfolio.",
            "What is happening in store S005?",
        ]

    if intent == "store_summary" and store_id:
        return [
            f"Explain {store_id} P0001",
            "Show top replenishment priorities.",
            "Summarize the portfolio.",
        ]

    if intent == "item_details" and store_id:
        return [
            f"What is happening in store {store_id}?",
            "Which items are highest risk this week?",
            "Summarize the portfolio.",
        ]

    return [
        "Summarize the portfolio.",
        "Which items are highest risk this week?",
        "Show top replenishment priorities.",
    ]


def route_query(user_query: str) -> dict:
    """
    Agent-style router:
    1. extract entities
    2. detect likely intent
    3. execute the chosen tool
    4. attach suggested follow-up questions
    """
    store_id = extract_store_id(user_query)
    product_id = extract_product_id(user_query)

    plan = detect_intent(user_query, store_id, product_id)
    intent = plan["intent"]
    reasoning = plan["reasoning"]

    result = execute_intent(intent, store_id, product_id)
    follow_ups = get_suggested_follow_ups(intent, store_id, product_id)

    return {
        "route": intent,
        "reasoning": reasoning,
        "entities": {
            "store_id": store_id,
            "product_id": product_id,
        },
        "suggested_follow_ups": follow_ups,
        "result": result,
    }