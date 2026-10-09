
from pathlib import Path

import pandas as pd
import streamlit as st


DATA_PATH = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "superstore.csv"
)


@st.cache_data(show_spinner=False)
def load_data(path=DATA_PATH):
    """Load and prepare the Global Superstore dataset."""

    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(
            f"Dataset not found: {path}\n"
            "Check that superstore.csv is inside the data folder."
        )

    # Load the dataset
    df = pd.read_csv(path, encoding="latin1")

    # Standardize column names:
    # Order.Date -> Order Date
    # Order_Date -> Order Date
    # order date -> Order Date
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.replace(".", " ", regex=False)
        .str.replace("_", " ", regex=False)
        .str.replace(r"\s+", " ", regex=True)
        .str.title()
    )

    # Handle common alternative column names
    aliases = {
        "Order Id": "Order ID",
        "Order Number": "Order ID",
        "Ship Date": "Ship Date",
        "Product": "Product Name",
        "Product": "Product Name",
        "Shipping Cost": "Shipping Cost",
        "Sub Category": "Sub-Category",
    }

    df = df.rename(columns=aliases)

    # Check required columns
    required = [
        "Order Date",
        "Ship Date",
        "Order ID",
        "Product Name",
        "Sales",
        "Profit",
        "Quantity",
        "Region",
        "Category",
    ]

    missing = [col for col in required if col not in df.columns]

    if missing:
        raise ValueError(
            f"Missing columns: {missing}\n"
            f"Available columns: {df.columns.tolist()}"
        )

    # Convert dates
    for col in ["Order Date", "Ship Date"]:
        df[col] = pd.to_datetime(
            df[col],
            errors="coerce"
        )

    # Convert numeric columns
    numeric_columns = [
        "Sales",
        "Profit",
        "Quantity",
        "Discount",
        "Shipping Cost",
    ]

    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(
                df[col],
                errors="coerce"
            )

    # Create date features
    df["Year"] = df["Order Date"].dt.year
    df["Month"] = df["Order Date"].dt.month
    df["Month Name"] = df["Order Date"].dt.strftime("%b")
    df["Year-Month"] = (
        df["Order Date"].dt.to_period("M").astype(str)
    )

    # Calculate shipping duration
    df["Shipping Days"] = (
        df["Ship Date"] - df["Order Date"]
    ).dt.days

    df.loc[df["Shipping Days"] < 0, "Shipping Days"] = float("nan")

    # Clean missing values in important text columns
    for col in [
        "Region",
        "Category",
        "Product Name",
        "Order ID",
    ]:
        df[col] = df[col].fillna("Unknown").astype(str)

    return df
