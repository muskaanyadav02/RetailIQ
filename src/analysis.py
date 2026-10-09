import pandas as pd
import numpy as np

def filtered_data(df, year="All", region="All", category="All"):
    out = df.copy()

    if year != "All":
        out = out[out["Year"] == int(year)]
    if region != "All":
        out = out[out["Region"] == region]
    if category != "All":
        out = out[out["Category"] == category]

    return out

def kpis(df):
    sales = df["Sales"].sum()
    profit = df["Profit"].sum()
    quantity = df["Quantity"].sum()
    orders = df["Order ID"].nunique() if "Order ID" in df else len(df)

    margin = (profit / sales * 100) if sales else 0
    aov = sales / orders if orders else 0
    shipping = df["Shipping Days"].dropna().mean() if "Shipping Days" in df else 0

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
    if df.empty:
        return pd.DataFrame(columns=["Year-Month", "Sales"])
    result = (
        df.groupby("Year-Month", as_index=False)["Sales"]
        .sum()
        .sort_values("Year-Month")
    )
    return result

def category_summary(df):
    return (
        df.groupby("Category", as_index=False)
        .agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"))
        .sort_values("Sales", ascending=False)
    )

def region_summary(df):
    return (
        df.groupby("Region", as_index=False)
        .agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"))
        .sort_values("Sales", ascending=False)
    )

def top_products(df, n=10):
    return (
        df.groupby("Product Name", as_index=False)["Profit"]
        .sum()
        .sort_values("Profit", ascending=False)
        .head(n)
    )

def subcategory_profit(df):
    return (
        df.groupby("Sub-Category", as_index=False)["Profit"]
        .sum()
        .sort_values("Profit")
    )

def insights(df):
    if df.empty:
        return [
            ("info", "No records match the selected filters."),
        ]

    cat = category_summary(df)
    reg = region_summary(df)
    products = top_products(df, 1)
    sub = subcategory_profit(df)
    k = kpis(df)

    items = []

    if not cat.empty:
        best_cat = cat.iloc[cat["Profit"].idxmax()]
        items.append(("success",
            f"{best_cat['Category']} is the most profitable category, "
            f"generating ${best_cat['Profit']:,.0f} in profit."
        ))

    if not reg.empty:
        best_reg = reg.iloc[reg["Sales"].idxmax()]
        items.append(("info",
            f"{best_reg['Region']} leads regional sales with "
            f"${best_reg['Sales']:,.0f} in revenue."
        ))

    if not products.empty:
        p = products.iloc[0]
        items.append(("success",
            f"{p['Product Name']} is the top product by profit at "
            f"${p['Profit']:,.0f}."
        ))

    if not sub.empty:
        worst = sub.iloc[0]
        if worst["Profit"] < 0:
            items.append(("warning",
                f"{worst['Sub-Category']} is currently loss-making with "
                f"${abs(worst['Profit']):,.0f} in negative profit."
            ))

    items.append(("neutral",
        f"Average order value is ${k['aov']:,.0f} and average shipping time "
        f"is {k['shipping']:.1f} days."
    ))

    return items
