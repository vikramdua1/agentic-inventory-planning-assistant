from __future__ import annotations

from pathlib import Path
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = BASE_DIR / "data" / "scored_forecasts.csv"


def load_forecasts() -> pd.DataFrame:
    """Load scored forecast data."""
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Forecast file not found: {DATA_PATH}")

    df = pd.read_csv(
        DATA_PATH,
        parse_dates=["week_start_date", "forecast_week_start_date"],
    )
    return df


def get_top_high_risk_items(top_n: int = 10) -> pd.DataFrame:
    """Return top high-risk items ranked by recommended order quantity."""
    df = load_forecasts()

    high_risk_df = df[df["stockout_risk"].str.lower() == "high"].copy()
    high_risk_df = high_risk_df.sort_values(
        ["recommended_order_qty", "predicted_next_week_units_sold"],
        ascending=False,
    )

    return high_risk_df.head(top_n)[
        [
            "store_id",
            "product_id",
            "predicted_next_week_units_sold",
            "reorder_point",
            "recommended_order_qty",
            "stockout_risk",
            "dominant_seasonality",
        ]
    ]


def get_top_replenishment_priorities(top_n: int = 10) -> pd.DataFrame:
    """Return top items by recommended order quantity."""
    df = load_forecasts()

    top_df = df.sort_values("recommended_order_qty", ascending=False).copy()

    return top_df.head(top_n)[
        [
            "store_id",
            "product_id",
            "predicted_next_week_units_sold",
            "reorder_point",
            "recommended_order_qty",
            "stockout_risk",
            "dominant_seasonality",
        ]
    ]


def get_store_summary(store_id: str) -> dict:
    """Return aggregated summary for a given store."""
    df = load_forecasts()

    store_df = df[df["store_id"].str.lower() == store_id.lower()].copy()

    if store_df.empty:
        return {"error": f"No records found for store_id={store_id}"}

    summary = {
        "store_id": store_id.upper(),
        "total_items": int(len(store_df)),
        "high_risk_items": int((store_df["stockout_risk"] == "high").sum()),
        "medium_risk_items": int((store_df["stockout_risk"] == "medium").sum()),
        "low_risk_items": int((store_df["stockout_risk"] == "low").sum()),
        "total_recommended_order_qty": round(float(store_df["recommended_order_qty"].sum()), 2),
        "avg_forecasted_demand": round(float(store_df["predicted_next_week_units_sold"].mean()), 2),
        "top_priority_items": (
            store_df.sort_values("recommended_order_qty", ascending=False)
            .head(5)[["product_id", "recommended_order_qty", "stockout_risk"]]
            .to_dict(orient="records")
        ),
    }

    return summary


def get_item_details(store_id: str, product_id: str) -> dict:
    """Return detailed explanation fields for a specific store-product pair."""
    df = load_forecasts()

    item_df = df[
        (df["store_id"].str.lower() == store_id.lower()) &
        (df["product_id"].str.lower() == product_id.lower())
    ].copy()

    if item_df.empty:
        return {"error": f"No record found for store_id={store_id}, product_id={product_id}"}

    row = item_df.iloc[0]

    demand_gap = round(
        float(row["predicted_next_week_units_sold"] - row["lag_1"]),
        2,
    )

    return {
        "store_id": row["store_id"],
        "product_id": row["product_id"],
        "forecast_week_start_date": str(row["forecast_week_start_date"]),
        "weekly_units_sold": round(float(row["weekly_units_sold"]), 2),
        "lag_1": round(float(row["lag_1"]), 2),
        "lag_2": round(float(row["lag_2"]), 2),
        "lag_4": round(float(row["lag_4"]), 2),
        "rolling_mean_4": round(float(row["rolling_mean_4"]), 2),
        "rolling_std_4": round(float(row["rolling_std_4"]), 2),
        "predicted_next_week_units_sold": round(float(row["predicted_next_week_units_sold"]), 2),
        "reorder_point": round(float(row["reorder_point"]), 2),
        "recommended_order_qty": round(float(row["recommended_order_qty"]), 2),
        "stockout_risk": row["stockout_risk"],
        "dominant_seasonality": row["dominant_seasonality"],
        "holiday_promotion_flag": int(row["holiday_promotion_flag"]),
        "demand_gap_vs_lag_1": demand_gap,
    }


def summarize_portfolio() -> dict:
    """Return overall portfolio summary statistics."""
    df = load_forecasts()

    summary = {
        "total_store_product_pairs": int(len(df)),
        "high_risk_items": int((df["stockout_risk"] == "high").sum()),
        "medium_risk_items": int((df["stockout_risk"] == "medium").sum()),
        "low_risk_items": int((df["stockout_risk"] == "low").sum()),
        "total_recommended_order_qty": round(float(df["recommended_order_qty"].sum()), 2),
        "avg_forecasted_demand": round(float(df["predicted_next_week_units_sold"].mean()), 2),
        "top_5_priority_items": (
            df.sort_values("recommended_order_qty", ascending=False)
            .head(5)[["store_id", "product_id", "recommended_order_qty", "stockout_risk"]]
            .to_dict(orient="records")
        ),
    }

    return summary