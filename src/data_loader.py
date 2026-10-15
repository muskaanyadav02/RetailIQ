
from pathlib import Path

import pandas as pd
import streamlit as st


DATA_PATH = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "superstore.csv"
)


def normalize_columns(df):
    df = df.copy()

    df.columns = [
        str(col).strip().replace(".", " ")
        for col in df.columns
    ]

    aliases = {
        "Sub Category": "Sub-Category",
        "Subcategory": "Sub-Category",
        "OrderDate": "Order Date",
        "ShipDate": "Ship Date",
        "CustomerName": "Customer Name",
        "CustomerID": "Customer ID",
        "OrderID": "Order ID",
        "ProductID": "Product ID",
        "ShipMode": "Ship Mode",
        "OrderPriority": "Order Priority",
        "ShippingCost": "Shipping Cost",
    }

    df = df.rename(
        columns={
            old: new
            for old, new in aliases.items()
            if old in df.columns and old != new
        }
    )

    df = df.loc[:, ~df.columns.duplicated()]

    return df


@st.cache_data(show_spinner="Loading retail data...")
def load_data():
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATA_PATH}"
        )

    try:
        df = pd.read_csv(
            DATA_PATH,
            encoding="utf-8-sig",
        )
    except UnicodeDecodeError:
        df = pd.read_csv(
            DATA_PATH,
            encoding="latin1",
        )

    df = normalize_columns(df)

    missing = [
        col for col in ["Sales", "Profit"]
        if col not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing required columns: {missing}. "
            f"Found: {df.columns.tolist()}"
        )

    for col in ["Order Date", "Ship Date"]:
        if col in df.columns:
            df[col] = pd.to_datetime(
                df[col],
                errors="coerce",
                dayfirst=False,
            )

    for col in [
        "Sales",
        "Profit",
        "Quantity",
        "Discount",
        "Shipping Cost",
    ]:
        if col in df.columns:
            df[col] = pd.to_numeric(
                df[col],
                errors="coerce",
            )

    text_columns = [
        "Region",
        "Category",
        "Sub-Category",
        "Product Name",
        "Country",
        "City",
        "State",
        "Segment",
        "Ship Mode",
        "Customer Name",
        "Order ID",
    ]

    for col in text_columns:
        if col in df.columns:
            df[col] = (
                df[col]
                .astype("string")
                .str.strip()
            )

    if "Order Date" in df.columns:
        df["Year"] = df["Order Date"].dt.year
        df["Month"] = df["Order Date"].dt.month
        df["Month Name"] = df["Order Date"].dt.strftime("%b")
        df["Year-Month"] = (
            df["Order Date"]
            .dt.to_period("M")
            .astype(str)
        )

    if {"Order Date", "Ship Date"}.issubset(df.columns):
        df["Shipping Days"] = (
            df["Ship Date"] - df["Order Date"]
        ).dt.total_seconds() / 86400

        df.loc[
            df["Shipping Days"] < 0,
            "Shipping Days",
        ] = float("nan")

    return df
