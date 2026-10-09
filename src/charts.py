import plotly.express as px
import plotly.graph_objects as go

BG = "#0b1220"
PANEL = "#111b2e"
GRID = "#26334a"
TEXT = "#e7eef9"
PRIMARY = "#62b6f7"
ACCENT = "#4f8cff"
PROFIT = "#22c55e"
LOSS = "#f87171"

def base_layout(fig, height=390):
    fig.update_layout(
        height=height,
        paper_bgcolor=BG,
        plot_bgcolor=BG,
        font=dict(color=TEXT, family="Arial"),
        margin=dict(l=45, r=25, t=55, b=45),
        hoverlabel=dict(bgcolor=PANEL, font_color=TEXT),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color=TEXT)
        ),
    )
    fig.update_xaxes(
        showgrid=False,
        linecolor=GRID,
        tickfont=dict(color=TEXT),
        title_font=dict(color=TEXT),
    )
    fig.update_yaxes(
        gridcolor=GRID,
        zerolinecolor=GRID,
        tickfont=dict(color=TEXT),
        title_font=dict(color=TEXT),
    )
    return fig

def monthly_sales_chart(data):
    fig = px.line(
        data,
        x="Year-Month",
        y="Sales",
        markers=True,
        title="Monthly Sales Trend",
    )
    fig.update_traces(
        line=dict(color=PRIMARY, width=3),
        marker=dict(size=7),
        hovertemplate="%{x}<br>Sales: $%{y:,.0f}<extra></extra>",
    )
    fig.update_layout(title_font_size=17)
    return base_layout(fig, 410)

def category_chart(data):
    fig = go.Figure()
    fig.add_bar(
        x=data["Category"],
        y=data["Sales"],
        name="Sales",
        marker_color=PRIMARY,
        text=data["Sales"],
        texttemplate="$%{text:.3s}",
        textposition="outside",
        hovertemplate="%{x}<br>Sales: $%{y:,.0f}<extra></extra>",
    )
    fig.add_bar(
        x=data["Category"],
        y=data["Profit"],
        name="Profit",
        marker_color=PROFIT,
        text=data["Profit"],
        texttemplate="$%{text:.3s}",
        textposition="outside",
        hovertemplate="%{x}<br>Profit: $%{y:,.0f}<extra></extra>",
    )
    fig.update_layout(
        title="Sales vs Profit by Category",
        barmode="group",
        yaxis_title="Amount",
    )
    return base_layout(fig, 410)

def region_chart(data):
    fig = px.bar(
        data,
        x="Region",
        y="Sales",
        text="Sales",
        title="Sales by Region",
    )
    fig.update_traces(
        marker_color=PRIMARY,
        texttemplate="$%{text:.3s}",
        textposition="outside",
        hovertemplate="%{x}<br>Sales: $%{y:,.0f}<extra></extra>",
    )
    fig.update_layout(xaxis_tickangle=-35)
    return base_layout(fig, 410)

def top_products_chart(data):
    data = data.sort_values("Profit", ascending=True)
    fig = px.bar(
        data,
        x="Profit",
        y="Product Name",
        orientation="h",
        text="Profit",
        title="Top 10 Products by Profit",
    )
    fig.update_traces(
        marker_color=PROFIT,
        texttemplate="$%{text:,.0f}",
        textposition="outside",
        hovertemplate="%{y}<br>Profit: $%{x:,.0f}<extra></extra>",
    )
    return base_layout(fig, 460)

def subcategory_chart(data):
    colors = [LOSS if x < 0 else PROFIT for x in data["Profit"]]
    fig = px.bar(
        data,
        x="Profit",
        y="Sub-Category",
        orientation="h",
        title="Profitability by Sub-Category",
    )
    fig.update_traces(
        marker_color=colors,
        hovertemplate="%{y}<br>Profit: $%{x:,.0f}<extra></extra>",
    )
    fig.add_vline(x=0, line_color=GRID, line_width=1)
    return base_layout(fig, 500)
