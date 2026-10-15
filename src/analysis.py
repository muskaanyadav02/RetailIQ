
import pandas as pd


def filtered_data(
    df,
    year="All",
    region="All",
    category="All",
):
    out = df.copy()

    if year != "All" and "Year" in out.columns:
        out = out[out["Year"] == int(year)]

    if region != "All" and "Region" in out.columns:
        out = out[out["Region"] == region]

    if category != "All" and "Category" in out.columns:
        out = out[out["Category"] == category]

    return out


def kpis(df):
    sales = float(df["Sales"].sum()) if "Sales" in df else 0.0
    profit = float(df["Profit"].sum()) if "Profit" in df else 0.0
    quantity = (
        float(df["Quantity"].sum())
        if "Quantity" in df.columns else 0.0
    )

    orders = (
        int(df["Order ID"].nunique())
        if "Order ID" in df.columns
        else len(df)
    )

    margin = profit / sales * 100 if sales else 0.0
    aov = sales / orders if orders else 0.0

    shipping = 0.0

    if "Shipping Days" in df.columns:
        average = df["Shipping Days"].mean()

        if pd.notna(average):
            shipping = float(average)

    return {
        "sales": sales,
        "profit": profit,
        "orders": orders,
        "margin": margin,
        "quantity": quantity,
        "aov": aov,
        "shipping": shipping,
    }


def monthly_sales(df):
    if not {"Year-Month", "Sales"}.issubset(df.columns):
        return pd.DataFrame(
            columns=["Year-Month", "Sales"]
        )

    return (
        df.groupby("Year-Month", as_index=False)["Sales"]
        .sum()
        .sort_values("Year-Month")
    )


def category_summary(df):
    if "Category" not in df.columns:
        return pd.DataFrame(
            columns=["Category", "Sales", "Profit"]
        )

    metrics = [
        col for col in ["Sales", "Profit", "Quantity"]
        if col in df.columns
    ]

    if not metrics:
        return pd.DataFrame(columns=["Category"])

    result = (
        df.groupby("Category", as_index=False)[metrics]
        .sum()
    )

    if "Sales" in result.columns:
        result = result.sort_values(
            "Sales",
            ascending=False,
        )

    return result


def region_summary(df):
    if "Region" not in df.columns:
        return pd.DataFrame(
            columns=["Region", "Sales", "Profit"]
        )

    metrics = [
        col for col in ["Sales", "Profit", "Quantity"]
        if col in df.columns
    ]

    if not metrics:
        return pd.DataFrame(columns=["Region"])

    result = (
        df.groupby("Region", as_index=False)[metrics]
        .sum()
    )

    if "Sales" in result.columns:
        result = result.sort_values(
            "Sales",
            ascending=False,
        )

    return result


def top_products(df, n=10, metric="Profit"):
    if df.empty or "Product Name" not in df.columns:
        return pd.DataFrame(
            columns=[
                "Product Name",
                "Sales",
                "Profit",
                "Quantity",
            ]
        )

    metrics = [
        col for col in ["Sales", "Profit", "Quantity"]
        if col in df.columns
    ]

    if not metrics:
        return pd.DataFrame(columns=["Product Name"])

    result = (
        df.groupby("Product Name", as_index=False)[metrics]
        .sum()
    )

    for col in ["Sales", "Profit", "Quantity"]:
        if col not in result.columns:
            result[col] = 0

    sort_by = metric if metric in metrics else metrics[0]

    return (
        result.sort_values(
            sort_by,
            ascending=False,
        )
        .head(n)
        .reset_index(drop=True)
    )


def subcategory_profit(df):
    if not {
        "Sub-Category",
        "Profit",
    }.issubset(df.columns):
        return pd.DataFrame(
            columns=["Sub-Category", "Profit"]
        )

    return (
        df.groupby("Sub-Category", as_index=False)["Profit"]
        .sum()
        .sort_values("Profit", ascending=True)
    )


def insights(df):
    if df.empty:
        return [
            ("warning", "No records match the current filters.")
        ]

    output = []

    categories = category_summary(df)

    if (
        not categories.empty
        and "Profit" in categories.columns
    ):
        best = categories.loc[
            categories["Profit"].idxmax()
        ]

        output.append((
            "success",
            f"{best['Category']} has the highest category "
            f"profit (${best['Profit']:,.2f}).",
        ))

    regions = region_summary(df)

    if (
        not regions.empty
        and "Sales" in regions.columns
    ):
        best = regions.loc[regions["Sales"].idxmax()]

        output.append((
            "info",
            f"{best['Region']} leads regional sales "
            f"(${best['Sales']:,.2f}).",
        ))

    products = top_products(df, 1, "Profit")

    if not products.empty:
        product = products.iloc[0]

        output.append((
            "success",
            f"Most profitable product: "
            f"{product['Product Name']} "
            f"(${product['Profit']:,.2f}).",
        ))

    subcategories = subcategory_profit(df)

    if not subcategories.empty:
        worst = subcategories.iloc[0]

        if worst["Profit"] < 0:
            output.append((
                "warning",
                f"{worst['Sub-Category']} is loss-making "
                f"(${worst['Profit']:,.2f}).",
            ))

    values = kpis(df)

    output.append((
        "neutral",
        f"Profit margin is {values['margin']:.2f}%, "
        f"with an average order value of "
        f"${values['aov']:,.2f}.",
    ))

    return output
