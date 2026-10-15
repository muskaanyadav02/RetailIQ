
import streamlit as st
import pandas as pd
import plotly.express as px

from src.data_loader import load_data
from src.analysis import (
    filtered_data,
    kpis,
    monthly_sales,
    category_summary,
    region_summary,
    top_products,
    subcategory_profit,
    insights,
)
from src.charts import (
    style_chart,
    empty_chart,
    category_chart,
    region_chart,
    top_products_chart,
    subcategory_chart,
)

# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="RetailIQ | Retail Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================================================
# DARK NAVY THEME
# =========================================================

st.markdown("""
<style>
.stApp {
    background: #0B1120;
    color: #E8EEF8;
}

[data-testid="stHeader"] {
    background: #0B1120;
}

[data-testid="stSidebar"] {
    background: #111B2E;
    border-right: 1px solid #293A55;
}

[data-testid="stSidebar"] * {
    color: #E3EBF7;
}

.block-container {
    max-width: 1500px;
    padding-top: 2.5rem !important;
    padding-bottom: 3rem;
}

h1, h2, h3, h4 {
    color: #F3F7FF !important;
    letter-spacing: -0.4px;
}

p, label {
    color: #C1CDE0;
}

[data-testid="stCaptionContainer"] {
    color: #91A5C1;
}

div[data-testid="stMetric"] {
    background: #16243A;
    border: 1px solid #2A3D5A;
    border-radius: 14px;
    padding: 18px;
    box-shadow: 0 5px 18px rgba(0,0,0,0.16);
}

div[data-testid="stMetricLabel"] {
    color: #AFC0D8;
}

div[data-testid="stMetricValue"] {
    color: #56B4FF;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    border-bottom: 1px solid #293A55;
}

.stTabs [data-baseweb="tab"] {
    color: #B9C8DD;
    padding: 12px 16px;
}

.stTabs [aria-selected="true"] {
    color: #67BDFF !important;
    border-bottom-color: #398BFA !important;
}

div[data-baseweb="select"] > div,
div[data-baseweb="input"] > div {
    background: #16243A;
    border-color: #344965;
    color: #F0F5FF;
}

input, textarea {
    color: #F0F5FF !important;
}

.stButton button,
.stDownloadButton button {
    background: #1D4ED8;
    color: #FFFFFF;
    border: 1px solid #3977F5;
    border-radius: 9px;
    font-weight: 650;
}

.stButton button:hover,
.stDownloadButton button:hover {
    background: #2563EB;
    border-color: #60A5FA;
    color: #FFFFFF;
}

[data-testid="stDataFrame"] {
    border: 1px solid #293A55;
    border-radius: 12px;
    overflow: hidden;
}

[data-testid="stVerticalBlockBorderWrapper"] {
    border-color: #293A55 !important;
    border-radius: 14px;
}

div[data-testid="stAlert"] {
    border-radius: 10px;
}

hr {
    border-color: #293A55 !important;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# HELPER FUNCTIONS
# =========================================================

@st.cache_data
def csv_bytes(frame):
    return frame.to_csv(index=False).encode("utf-8")


def show_chart(fig):
    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "displaylogo": False,
            "scrollZoom": False,
        },
    )


def search_frame(frame, columns, query):
    if not query.strip() or not columns:
        return frame

    mask = pd.Series(False, index=frame.index)

    for col in columns:
        mask |= frame[col].astype(str).str.contains(
            query.strip(),
            case=False,
            na=False,
            regex=False,
        )

    return frame[mask]


def money(value):
    return f"${value:,.0f}"


# =========================================================
# LOAD DATA
# =========================================================

try:
    df = load_data()

except Exception as exc:
    st.error("RetailIQ could not load the dataset.")
    st.code(str(exc))
    st.info(
        "Check that data/superstore.csv exists and "
        "contains Sales and Profit columns."
    )
    st.stop()

if df.empty:
    st.warning("The dataset is empty.")
    st.stop()

required = ["Sales", "Profit"]
missing = [col for col in required if col not in df.columns]

if missing:
    st.error(f"Missing required columns: {missing}")
    st.write("Detected columns:", df.columns.tolist())
    st.stop()


# =========================================================
# SIDEBAR FILTERS
# =========================================================

with st.sidebar:
    st.title("📊 RetailIQ")
    st.caption("RETAIL SALES INTELLIGENCE")
    st.divider()

    st.subheader("Explore the data")

    years = (
        sorted(df["Year"].dropna().astype(int).unique().tolist())
        if "Year" in df.columns else []
    )

    regions = (
        sorted(df["Region"].dropna().unique().tolist())
        if "Region" in df.columns else []
    )

    categories = (
        sorted(df["Category"].dropna().unique().tolist())
        if "Category" in df.columns else []
    )

    year = st.selectbox(
        "Order year",
        ["All"] + years,
        key="year_filter",
    )

    region = st.selectbox(
        "Region",
        ["All"] + regions,
        key="region_filter",
    )

    category = st.selectbox(
        "Category",
        ["All"] + categories,
        key="category_filter",
    )

    if (
        "Order Date" in df.columns
        and df["Order Date"].notna().any()
    ):
        min_date = df["Order Date"].min().date()
        max_date = df["Order Date"].max().date()

        date_range = st.date_input(
            "Order date range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
            key="date_filter",
        )
    else:
        min_date = max_date = None
        date_range = None

    def reset_filters():
        st.session_state["year_filter"] = "All"
        st.session_state["region_filter"] = "All"
        st.session_state["category_filter"] = "All"

        if min_date and max_date:
            st.session_state["date_filter"] = (
                min_date,
                max_date,
            )

    st.button(
        "↺ Reset all filters",
        on_click=reset_filters,
        use_container_width=True,
    )

    st.divider()

    st.caption("Dataset: Global Superstore")
    st.caption(f"{len(df):,} records available")

    st.download_button(
        "⬇ Download source data",
        data=csv_bytes(df),
        file_name="retailiq_source_data.csv",
        mime="text/csv",
        use_container_width=True,
    )


# =========================================================
# APPLY FILTERS
# =========================================================

data = filtered_data(df, year, region, category)

if (
    date_range
    and isinstance(date_range, (tuple, list))
    and len(date_range) == 2
    and "Order Date" in data.columns
):
    start = pd.Timestamp(date_range[0])
    end = pd.Timestamp(date_range[1]) + pd.Timedelta(days=1)

    data = data[
        (data["Order Date"] >= start)
        & (data["Order Date"] < end)
    ]


# =========================================================
# HEADER
# =========================================================

st.title("RetailIQ")
st.markdown(
    "**Retail Sales & Profit Intelligence**"
    "  ·  Interactive business analytics"
)

st.write(
    "Explore sales trends, product performance, regional results, "
    "and business opportunities using retail data."
)

st.caption(
    f"Showing {len(data):,} of {len(df):,} records"
    f"  ·  Year: {year}"
    f"  ·  Region: {region}"
    f"  ·  Category: {category}"
)

st.divider()

if data.empty:
    st.warning(
        "No records match the selected filters. "
        "Change your filters or reset them."
    )
    st.stop()


# =========================================================
# KPI CARDS
# =========================================================

k = kpis(data)

st.subheader("Business at a glance")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Sales", money(k["sales"]))
c2.metric("Total Profit", money(k["profit"]))
c3.metric("Unique Orders", f"{k['orders']:,}")
c4.metric("Profit Margin", f"{k['margin']:.2f}%")

c5, c6, c7 = st.columns(3)

c5.metric("Units Sold", f"{k['quantity']:,.0f}")
c6.metric("Average Order Value", f"${k['aov']:,.2f}")
c7.metric("Avg. Shipping Time", f"{k['shipping']:.1f} days")


# =========================================================
# DASHBOARD TABS
# =========================================================

overview, products, business, explorer = st.tabs([
    "📈 Overview",
    "🔎 Product Explorer",
    "💡 Business Insights",
    "📋 Data Explorer",
])


# =========================================================
# OVERVIEW
# =========================================================

with overview:
    st.subheader("Sales performance")

    metric = st.selectbox(
        "Select trend metric",
        ["Sales", "Profit", "Orders", "Quantity"],
        key="overview_metric",
    )

    if "Year-Month" not in data.columns:
        show_chart(empty_chart("Monthly Performance"))

    else:
        if metric == "Orders" and "Order ID" in data.columns:
            trend = (
                data.groupby("Year-Month")["Order ID"]
                .nunique()
                .reset_index(name="Orders")
            )
            y_col = "Orders"

        elif metric in data.columns:
            trend = (
                data.groupby("Year-Month")[metric]
                .sum()
                .reset_index()
            )
            y_col = metric

        else:
            trend = pd.DataFrame()
            y_col = None

        if not trend.empty and y_col:
            trend = trend.sort_values("Year-Month")

            chart_type = st.radio(
                "Chart style",
                ["Line", "Area", "Bar"],
                horizontal=True,
                key="trend_chart_type",
            )

            if chart_type == "Line":
                fig = px.line(
                    trend,
                    x="Year-Month",
                    y=y_col,
                    markers=True,
                    title=f"Monthly {metric}",
                    color_discrete_sequence=["#4EA8FF"],
                )
                fig.update_traces(line_width=3)

            elif chart_type == "Area":
                fig = px.area(
                    trend,
                    x="Year-Month",
                    y=y_col,
                    title=f"Monthly {metric}",
                    color_discrete_sequence=["#3977D5"],
                )

            else:
                fig = px.bar(
                    trend,
                    x="Year-Month",
                    y=y_col,
                    title=f"Monthly {metric}",
                    color_discrete_sequence=["#4EA8FF"],
                )

            fig.update_traces(
                hovertemplate=(
                    "%{x}<br>%{y:,.2f}<extra></extra>"
                )
            )

            show_chart(style_chart(fig, 420))

        else:
            st.info("This metric is unavailable.")

    st.subheader("Category and regional performance")

    left, right = st.columns(2)

    with left:
        show_chart(category_chart(category_summary(data)))

    with right:
        show_chart(region_chart(region_summary(data)))

    st.subheader("Profitability and sales mix")

    left, right = st.columns(2)

    with left:
        show_chart(subcategory_chart(subcategory_profit(data)))

    with right:
        summary = category_summary(data)

        if (
            not summary.empty
            and {"Category", "Sales"}.issubset(summary.columns)
        ):
            fig = px.pie(
                summary,
                names="Category",
                values="Sales",
                hole=0.58,
                title="Share of Sales by Category",
                color_discrete_sequence=[
                    "#4EA8FF",
                    "#22D3B4",
                    "#9B8AFB",
                    "#F5B84B",
                ],
            )

            show_chart(style_chart(fig, 390))

        else:
            show_chart(empty_chart("Share of Sales by Category"))


# =========================================================
# PRODUCT EXPLORER
# =========================================================

with products:
    st.subheader("Discover product performance")

    st.write(
        "Search products, rank performers, and export the results."
    )

    if "Product Name" not in data.columns:
        st.warning("Product Name is not available.")

    else:
        query = st.text_input(
            "Search products",
            placeholder="Search for chairs, phones, tables...",
            key="product_search",
        )

        product_data = data.copy()

        if query.strip():
            product_data = product_data[
                product_data["Product Name"].astype(str).str.contains(
                    query.strip(),
                    case=False,
                    na=False,
                    regex=False,
                )
            ]

        metrics = [
            col for col in ["Sales", "Profit", "Quantity"]
            if col in product_data.columns
        ]

        if not metrics:
            st.warning("No product metrics are available.")

        else:
            selected_metric = st.selectbox(
                "Rank products by",
                metrics,
                key="product_metric",
            )

            ranking = st.radio(
                "Performance",
                ["Top performers", "Bottom performers"],
                horizontal=True,
            )

            limit = st.slider(
                "Number of products",
                min_value=5,
                max_value=25,
                value=10,
                step=5,
                key="product_limit",
            )

            summary = top_products(
                product_data,
                n=len(product_data),
                metric=selected_metric,
            )

            if not summary.empty:
                summary = (
                    summary.sort_values(
                        selected_metric,
                        ascending=(ranking == "Bottom performers"),
                    )
                    .head(limit)
                    .reset_index(drop=True)
                )

                show_chart(top_products_chart(summary))

                st.dataframe(
                    summary,
                    use_container_width=True,
                    hide_index=True,
                )

                st.download_button(
                    "⬇ Download product analysis",
                    data=csv_bytes(summary),
                    file_name="retailiq_product_analysis.csv",
                    mime="text/csv",
                )

            else:
                st.info("No matching products found.")


# =========================================================
# BUSINESS INSIGHTS
# =========================================================

with business:
    st.subheader("Automated business insights")

    st.write(
        "Observations below are calculated from your selected data."
    )

    icons = {
        "success": "🏆",
        "info": "📊",
        "warning": "⚠️",
        "neutral": "💡",
    }

    for kind, message in insights(data):
        icon = icons.get(kind, "💡")

        if kind == "warning":
            st.warning(f"{icon} {message}")
        elif kind == "success":
            st.success(f"{icon} {message}")
        elif kind == "info":
            st.info(f"{icon} {message}")
        else:
            st.write(f"{icon} {message}")

    st.subheader("Compare regional performance")

    regions_df = region_summary(data)

    if not regions_df.empty:
        options = [
            col for col in ["Sales", "Profit", "Quantity"]
            if col in regions_df.columns
        ]

        if options:
            region_metric = st.selectbox(
                "Regional metric",
                options,
                key="region_compare_metric",
            )

            fig = px.bar(
                regions_df.sort_values(
                    region_metric,
                    ascending=False,
                ),
                x="Region",
                y=region_metric,
                color=region_metric,
                color_continuous_scale=[
                    "#244A78",
                    "#4EA8FF",
                ],
                title=f"Regions ranked by {region_metric}",
            )

            fig.update_layout(coloraxis_showscale=False)

            show_chart(style_chart(fig, 400))

    else:
        st.info("Regional data is unavailable.")


# =========================================================
# DATA EXPLORER
# =========================================================

with explorer:
    st.subheader("Explore underlying records")

    st.write(
        "Search filtered records, customize columns, and download results."
    )

    searchable_columns = [
        col for col in [
            "Order ID",
            "Customer Name",
            "Product Name",
            "City",
            "State",
            "Country",
        ]
        if col in data.columns
    ]

    search = st.text_input(
        "Search records",
        placeholder="Search customers, products, orders, or locations...",
        key="data_search",
    )

    view = search_frame(
        data.copy(),
        searchable_columns,
        search,
    )

    defaults = [
        col for col in [
            "Order Date",
            "Order ID",
            "Customer Name",
            "Region",
            "Category",
            "Sub-Category",
            "Product Name",
            "Sales",
            "Profit",
            "Quantity",
        ]
        if col in view.columns
    ]

    selected_columns = st.multiselect(
        "Columns to display",
        options=list(view.columns),
        default=defaults,
        key="display_columns",
    )

    st.caption(f"{len(view):,} matching records")

    st.dataframe(
        view[selected_columns],
        use_container_width=True,
        height=430,
        hide_index=True,
    )

    st.download_button(
        "⬇ Download filtered records",
        data=csv_bytes(view[selected_columns]),
        file_name="retailiq_filtered_records.csv",
        mime="text/csv",
    )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "RetailIQ  |  Interactive Retail Analytics  |  "
    "Python · Pandas · Plotly · Streamlit"
)
