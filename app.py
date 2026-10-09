import streamlit as st
import pandas as pd

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
    monthly_sales_chart,
    category_chart,
    region_chart,
    top_products_chart,
    subcategory_chart,
)

# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(
    page_title="RetailIQ | Sales Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------
# PROFESSIONAL CSS
# ---------------------------------------------------------
st.markdown("""
<style>
    .stApp {
        background: #080f1d;
        color: #e7eef9;
    }

    [data-testid="stSidebar"] {
        background: #0e1728;
        border-right: 1px solid #22304a;
    }

    [data-testid="stSidebar"] * {
        color: #dbe7f7;
    }

    .block-container {
        max-width: 1450px;
        padding-top: 2.2rem;
        padding-bottom: 3rem;
    }

    h1, h2, h3 {
        letter-spacing: -0.4px;
    }

    .brand {
        font-size: 30px;
        font-weight: 800;
        margin-bottom: 2px;
    }

    .brand-sub {
        color: #7ea6d4;
        font-size: 13px;
        margin-bottom: 30px;
    }

    .eyebrow {
        display: inline-block;
        padding: 7px 14px;
        border-radius: 999px;
        background: #10285a;
        border: 1px solid #2457b7;
        color: #64b5ff;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: .5px;
        margin-bottom: 12px;
    }

    .hero-title {
        font-size: 42px;
        line-height: 1.05;
        font-weight: 850;
        margin: 0;
    }

    .hero-subtitle {
        color: #8da9ca;
        font-size: 16px;
        margin-top: 8px;
        margin-bottom: 25px;
    }

    .filter-banner {
        background: linear-gradient(90deg, #122b50, #10233f);
        border: 1px solid #1e477c;
        padding: 15px 18px;
        border-radius: 12px;
        color: #6ec1ff;
        font-weight: 600;
        margin-bottom: 18px;
    }

    .kpi-card {
        background: linear-gradient(145deg, #121e33, #0e1728);
        border: 1px solid #263750;
        border-radius: 15px;
        padding: 20px 21px;
        min-height: 132px;
        box-shadow: 0 10px 25px rgba(0,0,0,.16);
    }

    .kpi-label {
        color: #8db1d9;
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: .5px;
    }

    .kpi-value {
        color: #f4f8ff;
        font-size: 29px;
        font-weight: 800;
        margin-top: 9px;
    }

    .kpi-note {
        color: #607d9f;
        font-size: 12px;
        margin-top: 5px;
    }

    .section-title {
        font-size: 22px;
        font-weight: 800;
        margin-top: 28px;
        margin-bottom: 13px;
    }

    .insight-card {
        background: #101a2c;
        border: 1px solid #253650;
        border-radius: 11px;
        padding: 14px 17px;
        margin: 9px 0;
        color: #dbe7f7;
        font-size: 14px;
    }

    .insight-success { border-left: 4px solid #22c55e; }
    .insight-info { border-left: 4px solid #38bdf8; }
    .insight-warning { border-left: 4px solid #f59e0b; }
    .insight-neutral { border-left: 4px solid #64748b; }

    .side-stat {
        border-top: 1px solid #263650;
        margin-top: 24px;
        padding-top: 18px;
        color: #7796bb;
        font-size: 12px;
        line-height: 1.8;
    }

    .footer {
        border-top: 1px solid #22304a;
        margin-top: 45px;
        padding-top: 18px;
        color: #657f9e;
        font-size: 12px;
        text-align: center;
    }

    .stDownloadButton button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------
try:
    df = load_data()
except Exception as e:
    st.error(
        "Unable to load the dataset. Make sure "
        "`data/superstore.csv` exists."
    )
    st.exception(e)
    st.stop()

# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------
with st.sidebar:
    st.markdown('<div class="brand">📊 RetailIQ</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="brand-sub">Sales & Profit Intelligence</div>',
        unsafe_allow_html=True
    )

    st.markdown("### 🔎 Dashboard Filters")

    years = sorted(df["Year"].dropna().unique().astype(int).tolist())
    regions = sorted(df["Region"].dropna().unique().tolist())
    categories = sorted(df["Category"].dropna().unique().tolist())

    selected_year = st.selectbox(
        "📅 Year",
        ["All"] + years,
        index=0,
    )
    selected_region = st.selectbox(
        "🌍 Region",
        ["All"] + regions,
        index=0,
    )
    selected_category = st.selectbox(
        "📦 Category",
        ["All"] + categories,
        index=0,
    )

    st.markdown(
        f"""
        <div class="side-stat">
            <b>Dataset</b><br>
            Global Superstore<br><br>
            <b>Records</b><br>
            {len(df):,} transactions<br><br>
            <b>Analytics</b><br>
            Sales • Profit • Products<br>
            Regions • Shipping
        </div>
        """,
        unsafe_allow_html=True
    )

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Download Full Dataset",
        data=csv,
        file_name="retailiq_superstore.csv",
        mime="text/csv",
    )

# ---------------------------------------------------------
# FILTER DATA
# ---------------------------------------------------------
data = filtered_data(
    df,
    selected_year,
    selected_region,
    selected_category,
)

k = kpis(data)

year_text = str(selected_year)
region_text = str(selected_region)
category_text = str(selected_category)

st.markdown('<div class="eyebrow">DATA ANALYTICS PROJECT</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-title">RetailIQ</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="hero-subtitle">Sales & Profit Intelligence Dashboard</div>',
    unsafe_allow_html=True
)

st.markdown(
    f"""
    <div class="filter-banner">
        🔎 Active Filters &nbsp;—&nbsp;
        Year: {year_text} &nbsp;|&nbsp;
        Region: {region_text} &nbsp;|&nbsp;
        Category: {category_text}
    </div>
    """,
    unsafe_allow_html=True
)

# ---------------------------------------------------------
# KPI CARDS
# ---------------------------------------------------------
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(
        f"""<div class="kpi-card">
        <div class="kpi-label">💰 Total Sales</div>
        <div class="kpi-value">${k['sales']:,.0f}</div>
        <div class="kpi-note">Revenue generated</div>
        </div>""",
        unsafe_allow_html=True
    )

with c2:
    st.markdown(
        f"""<div class="kpi-card">
        <div class="kpi-label">📈 Total Profit</div>
        <div class="kpi-value">${k['profit']:,.0f}</div>
        <div class="kpi-note">Net profit generated</div>
        </div>""",
        unsafe_allow_html=True
    )

with c3:
    st.markdown(
        f"""<div class="kpi-card">
        <div class="kpi-label">🛒 Total Orders</div>
        <div class="kpi-value">{k['orders']:,}</div>
        <div class="kpi-note">Unique customer orders</div>
        </div>""",
        unsafe_allow_html=True
    )

with c4:
    st.markdown(
        f"""<div class="kpi-card">
        <div class="kpi-label">📊 Profit Margin</div>
        <div class="kpi-value">{k['margin']:.2f}%</div>
        <div class="kpi-note">Overall profitability</div>
        </div>""",
        unsafe_allow_html=True
    )

# ---------------------------------------------------------
# OPERATIONAL OVERVIEW
# ---------------------------------------------------------
st.markdown('<div class="section-title">📌 Operational Overview</div>', unsafe_allow_html=True)

o1, o2, o3 = st.columns(3)

with o1:
    st.metric("📦 Total Quantity", f"{k['quantity']:,.0f}")

with o2:
    st.metric("💳 Average Order Value", f"${k['aov']:,.0f}")

with o3:
    st.metric("🚚 Average Shipping Time", f"{k['shipping']:.1f} days")

# ---------------------------------------------------------
# SALES PERFORMANCE
# ---------------------------------------------------------
st.markdown('<div class="section-title">📈 Sales Performance</div>', unsafe_allow_html=True)

monthly = monthly_sales(data)
st.plotly_chart(
    monthly_sales_chart(monthly),
    use_container_width=True,
    config={"displaylogo": False},
)

# ---------------------------------------------------------
# CATEGORY + REGION
# ---------------------------------------------------------
left, right = st.columns(2)

with left:
    cat = category_summary(data)
    st.plotly_chart(
        category_chart(cat),
        use_container_width=True,
        config={"displaylogo": False},
    )

with right:
    reg = region_summary(data)
    st.plotly_chart(
        region_chart(reg),
        use_container_width=True,
        config={"displaylogo": False},
    )

# ---------------------------------------------------------
# PRODUCT + SUBCATEGORY
# ---------------------------------------------------------
st.markdown('<div class="section-title">🏆 Product & Profitability Analysis</div>', unsafe_allow_html=True)

left, right = st.columns(2)

with left:
    products = top_products(data, 10)
    st.plotly_chart(
        top_products_chart(products),
        use_container_width=True,
        config={"displaylogo": False},
    )

with right:
    sub = subcategory_profit(data)
    st.plotly_chart(
        subcategory_chart(sub),
        use_container_width=True,
        config={"displaylogo": False},
    )

# ---------------------------------------------------------
# BUSINESS INSIGHTS
# ---------------------------------------------------------
st.markdown('<div class="section-title">💡 Business Insights</div>', unsafe_allow_html=True)

for kind, message in insights(data):
    icon = {
        "success": "🏆",
        "info": "🌍",
        "warning": "⚠️",
        "neutral": "🚚",
    }.get(kind, "•")

    st.markdown(
        f'<div class="insight-card insight-{kind}">{icon}&nbsp;&nbsp;{message}</div>',
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------
# FILTERED DATA PREVIEW
# ---------------------------------------------------------
st.markdown('<div class="section-title">🗂️ Filtered Dataset</div>', unsafe_allow_html=True)

with st.expander(f"View filtered records ({len(data):,})"):
    st.dataframe(
        data,
        use_container_width=True,
        height=430,
        hide_index=True,
    )

    filtered_csv = data.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Download Filtered Data",
        data=filtered_csv,
        file_name="retailiq_filtered_data.csv",
        mime="text/csv",
    )

# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------
st.markdown(
    """
    <div class="footer">
        <b>RetailIQ — Sales & Profit Intelligence Dashboard</b><br>
        Data Analytics Project • Built with Python, Pandas, Plotly & Streamlit<br>
        Developed for academic demonstration and business analytics
    </div>
    """,
    unsafe_allow_html=True
)
