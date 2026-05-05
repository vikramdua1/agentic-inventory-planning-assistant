from __future__ import annotations


def format_portfolio_summary(summary: dict) -> str:
    return f"""
Portfolio Summary

Total store-product pairs: {summary['total_store_product_pairs']}
High-risk items: {summary['high_risk_items']}
Medium-risk items: {summary['medium_risk_items']}
Low-risk items: {summary['low_risk_items']}
Total recommended order quantity: {summary['total_recommended_order_qty']}
Average forecasted demand: {summary['avg_forecasted_demand']}

Top 5 priority items:
{_format_priority_list(summary['top_5_priority_items'])}
""".strip()


def get_portfolio_manager_interpretation(summary: dict) -> str:
    high_risk = summary["high_risk_items"]
    medium_risk = summary["medium_risk_items"]
    total_qty = summary["total_recommended_order_qty"]
    avg_forecast = summary["avg_forecasted_demand"]

    return (
        f"The portfolio currently contains {high_risk} high-risk items and {medium_risk} medium-risk items. "
        f"Total recommended replenishment volume is {total_qty}, with average forecasted demand at {avg_forecast}. "
        f"Planning attention should first go to the top five priority items, especially where recommended order quantities are highest."
    )


def format_store_summary(summary: dict) -> str:
    if "error" in summary:
        return summary["error"]

    return f"""
Store Summary: {summary['store_id']}

Total items: {summary['total_items']}
High-risk items: {summary['high_risk_items']}
Medium-risk items: {summary['medium_risk_items']}
Low-risk items: {summary['low_risk_items']}
Total recommended order quantity: {summary['total_recommended_order_qty']}
Average forecasted demand: {summary['avg_forecasted_demand']}

Top priority items:
{_format_store_priority_list(summary['top_priority_items'])}
""".strip()


def get_store_manager_interpretation(summary: dict) -> str:
    if "error" in summary:
        return summary["error"]

    if summary["high_risk_items"] >= 5:
        return (
            f"Store {summary['store_id']} shows a meaningful concentration of high-risk items. "
            f"Immediate replenishment review is recommended for the top-priority products listed."
        )
    elif summary["high_risk_items"] > 0:
        return (
            f"Store {summary['store_id']} has some elevated replenishment risk, but the situation appears manageable "
            f"if attention is given to the highest-priority items."
        )

    return (
        f"Store {summary['store_id']} currently appears relatively stable, with limited immediate stockout pressure."
    )


def format_item_details(details: dict) -> str:
    if "error" in details:
        return details["error"]

    return f"""
Item Detail: {details['store_id']} - {details['product_id']}

Forecast week start: {details['forecast_week_start_date']}
Current week units sold: {details['weekly_units_sold']}
Lag 1: {details['lag_1']}
Lag 2: {details['lag_2']}
Lag 4: {details['lag_4']}
Rolling mean (4): {details['rolling_mean_4']}
Rolling std (4): {details['rolling_std_4']}
Predicted next week units sold: {details['predicted_next_week_units_sold']}
Reorder point: {details['reorder_point']}
Recommended order quantity: {details['recommended_order_qty']}
Stockout risk: {details['stockout_risk']}
Dominant seasonality: {details['dominant_seasonality']}
Holiday/Promotion flag: {details['holiday_promotion_flag']}
Demand gap vs lag 1: {details['demand_gap_vs_lag_1']}
""".strip()


def get_item_manager_interpretation(details: dict) -> str:
    if "error" in details:
        return details["error"]

    risk = details["stockout_risk"].lower()
    demand_gap = details["demand_gap_vs_lag_1"]
    reorder_qty = details["recommended_order_qty"]

    if risk == "high":
        return (
            f"This item appears at meaningful stockout risk. Forecasted demand is running {demand_gap} units above lag-1 demand, "
            f"and the current recommendation is to order {reorder_qty} units."
        )
    elif risk == "medium":
        return (
            f"This item should be monitored closely. Forecasted demand is above recent demand, and a replenishment action of "
            f"{reorder_qty} units is recommended to reduce short-term risk."
        )

    return (
        f"This item currently looks relatively stable. Recent demand appears sufficient versus forecast, "
        f"and immediate replenishment pressure is lower."
    )


def format_table_result(title: str, rows: list[dict]) -> str:
    if not rows:
        return f"{title}\n\nNo records found."

    lines = [title, ""]
    for i, row in enumerate(rows, start=1):
        lines.append(
            f"{i}. Store {row['store_id']} | Product {row['product_id']} | "
            f"Forecast: {row['predicted_next_week_units_sold']} | "
            f"Reorder Point: {row['reorder_point']} | "
            f"Recommended Qty: {row['recommended_order_qty']} | "
            f"Risk: {row['stockout_risk']} | "
            f"Seasonality: {row['dominant_seasonality']}"
        )
    return "\n".join(lines)


def get_table_manager_interpretation(title: str, rows: list[dict]) -> str:
    if not rows:
        return "No immediate planning recommendation is available because no records were returned."

    top_row = rows[0]
    return (
        f"For immediate action, start with Store {top_row['store_id']} / Product {top_row['product_id']}, "
        f"which has recommended order quantity {top_row['recommended_order_qty']} and risk level {top_row['stockout_risk']}. "
        f"The rest of the listed items should be reviewed in descending order of replenishment priority."
    )


def _format_priority_list(items: list[dict]) -> str:
    if not items:
        return "No priority items found."

    lines = []
    for i, item in enumerate(items, start=1):
        lines.append(
            f"{i}. Store {item['store_id']} | Product {item['product_id']} | "
            f"Recommended Qty: {item['recommended_order_qty']} | Risk: {item['stockout_risk']}"
        )
    return "\n".join(lines)


def _format_store_priority_list(items: list[dict]) -> str:
    if not items:
        return "No priority items found."

    lines = []
    for i, item in enumerate(items, start=1):
        lines.append(
            f"{i}. Product {item['product_id']} | Recommended Qty: {item['recommended_order_qty']} | "
            f"Risk: {item['stockout_risk']}"
        )
    return "\n".join(lines)