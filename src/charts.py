
import plotly.express as px
import plotly.graph_objects as go


BG = "#111B2E"
TEXT = "#E8EEF8"
GRID = "#2B3B55"

BLUE = "#4EA8FF"
TEAL = "#22D3B4"
VIOLET = "#9B8AFB"
ORANGE = "#F5B84B"
RED = "#FF6B78"


def style_chart(fig, height=380):
    fig.update_layout(
        height=height,
        paper_bgcolor=BG,
        plot_bgcolor=BG,
        font=dict(
            family="Arial",
            color=TEXT,
            size=12,
        ),
        title=dict(
            font=dict(size=17, color="#F3F7FF"),
        ),
        margin=dict(l=35, r=35, t=65, b=45),
        hoverlabel=dict(
            bgcolor="#243550",
            bordercolor="#405878",
            font_color="#FFFFFF",
        ),
        legend=dict(
            bgcolor="rgba(17,27,46,0)",
            font=dict(color=TEXT),
        ),
    )

    fig.update_xaxes(
        showgrid=False,
        linecolor=GRID,
        tickfont=dict(color=TEXT),
        title_font=dict(color=TEXT),
        zerolinecolor=GRID,
    )

    fig.update_yaxes(
        gridcolor=GRID,
        linecolor=GRID,
        tickfont=dict(color=TEXT),
        title_font=dict(color=TEXT),
        zerolinecolor=GRID,
    )

    return fig


def empty_chart(
    title,
    message="No data available for this selection.",
):
    fig = go.Figure()

    fig.add_annotation(
        text=message,
        x=0.5,
        y=0.5,
        xref="paper",
        yref="paper",
        showarrow=False,
        font=dict(size=13, color="#AFC0D8"),
    )

    fig.update_layout(title=title)

    return style_chart(fig, 350)


def monthly_sales_chart(data):
    if data.empty or not {
        "Year-Month",
        "Sales",
    }.issubset(data.columns):
        return empty_chart("Monthly Sales Trend")

    fig = px.line(
        data,
        x="Year-Month",
        y="Sales",
        markers=True,
        title="Monthly Sales Trend",
        color_discrete_sequence=[BLUE],
    )

    fig.update_traces(
        line=dict(width=3),
        marker=dict(size=7),
        hovertemplate=(
            "%{x}<br>Sales: $%{y:,.2f}<extra></extra>"
        ),
    )

    return style_chart(fig, 390)


def category_chart(data):
    if data.empty or "Category" not in data.columns:
        return empty_chart("Sales and Profit by Category")

    fig = go.Figure()

    if "Sales" in data.columns:
        fig.add_bar(
            x=data["Category"],
            y=data["Sales"],
            name="Sales",
            marker_color=BLUE,
            hovertemplate=(
                "%{x}<br>Sales: $%{y:,.2f}<extra></extra>"
            ),
        )

    if "Profit" in data.columns:
        fig.add_bar(
            x=data["Category"],
            y=data["Profit"],
            name="Profit",
            marker_color=TEAL,
            hovertemplate=(
                "%{x}<br>Profit: $%{y:,.2f}<extra></extra>"
            ),
        )

    fig.update_layout(
        title="Sales vs Profit by Category",
        barmode="group",
        yaxis_title="Amount ($)",
    )

    return style_chart(fig, 390)


def region_chart(data):
    if data.empty or not {
        "Region",
        "Sales",
    }.issubset(data.columns):
        return empty_chart("Sales by Region")

    data = data.sort_values(
        "Sales",
        ascending=True,
    )

    fig = px.bar(
        data,
        x="Sales",
        y="Region",
        orientation="h",
        title="Sales by Region",
        text="Sales",
        color="Sales",
        color_continuous_scale=[
            "#244A78",
            BLUE,
        ],
    )

    fig.update_traces(
        texttemplate="$%{text:,.0f}",
        textposition="outside",
        cliponaxis=False,
        hovertemplate=(
            "%{y}<br>Sales: $%{x:,.2f}<extra></extra>"
        ),
    )

    fig.update_layout(
        coloraxis_showscale=False,
    )

    return style_chart(
        fig,
        max(360, len(data) * 34),
    )


def top_products_chart(data):
    if data.empty or "Product Name" not in data.columns:
        return empty_chart("Top Products")

    metric = (
        "Profit"
        if "Profit" in data.columns
        else "Sales"
    )

    if metric not in data.columns:
        return empty_chart("Top Products")

    data = data.sort_values(
        metric,
        ascending=True,
    )

    fig = px.bar(
        data,
        x=metric,
        y="Product Name",
        orientation="h",
        title=f"Products by {metric}",
        color=metric,
        color_continuous_scale=[
            "#244A78",
            BLUE,
        ],
        hover_data=[
            col for col in ["Sales", "Profit", "Quantity"]
            if col in data.columns
        ],
    )

    fig.update_layout(
        coloraxis_showscale=False,
    )

    return style_chart(
        fig,
        max(400, len(data) * 30),
    )


def subcategory_chart(data):
    if not {
        "Sub-Category",
        "Profit",
    }.issubset(data.columns):
        return empty_chart("Profitability by Sub-Category")

    if data.empty:
        return empty_chart("Profitability by Sub-Category")

    data = data.sort_values(
        "Profit",
        ascending=True,
    )

    colors = [
        RED if value < 0 else TEAL
        for value in data["Profit"]
    ]

    fig = go.Figure(
        go.Bar(
            x=data["Profit"],
            y=data["Sub-Category"],
            orientation="h",
            marker_color=colors,
            hovertemplate=(
                "%{y}<br>Profit: $%{x:,.2f}<extra></extra>"
            ),
        )
    )

    fig.add_vline(
        x=0,
        line_color=GRID,
        line_width=1,
    )

    fig.update_layout(
        title="Profitability by Sub-Category",
        xaxis_title="Profit ($)",
    )

    return style_chart(
        fig,
        max(400, len(data) * 28),
    )
