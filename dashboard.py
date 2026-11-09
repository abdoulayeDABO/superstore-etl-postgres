from functools import lru_cache

import streamlit as st

st.set_page_config(page_title="Sales Dashboard", layout="wide")
st.title("Sales Dashboard")
st.markdown("An interactive dashboard to explore sales performance.")

conn = st.connection("postgresql", type="sql")


# ---------------------------------------------------------------
# Queries
# ---------------------------------------------------------------
@lru_cache(maxsize=1)
def get_kpis() -> dict:
    """Return the global KPIs computed from the orders table."""
    df = conn.query(
        """
        SELECT
            COUNT(DISTINCT order_id)    AS total_orders,
            SUM(sales)                  AS total_sales,
            SUM(profit)                 AS total_profit,
            COUNT(DISTINCT customer_id) AS total_customers
        FROM orders;
        """,
        ttl=0,
    )
    return df.iloc[0].to_dict()


@lru_cache(maxsize=1)
def get_monthly():
    """Return KPIs aggregated by month (used for sparklines and deltas)."""
    df = conn.query(
        """
        SELECT
            DATE_TRUNC('month', order_date) AS month,
            COUNT(DISTINCT order_id)        AS orders,
            SUM(sales)                      AS sales,
            SUM(profit)                     AS profit,
            COUNT(DISTINCT customer_id)     AS customers
        FROM orders
        GROUP BY 1
        ORDER BY 1;
        """,
        ttl=0,
    )
    # Decimal -> float for all numeric columns
    for col in ["orders", "sales", "profit", "customers"]:
        df[col] = df[col].astype(float)

    # Derived monthly metrics
    df["avg_basket"] = df["sales"] / df["orders"]
    df["margin"] = df["profit"] / df["sales"]
    return df


@lru_cache(maxsize=1)
def get_by_region():
    """Return sales and profit aggregated by region."""
    df = conn.query(
        """
        SELECT
            region,
            SUM(sales)  AS sales,
            SUM(profit) AS profit
        FROM orders
        GROUP BY region
        ORDER BY sales DESC;
        """,
        ttl=0,
    )
    df[["sales", "profit"]] = df[["sales", "profit"]].astype(float)
    return df


@lru_cache(maxsize=1)
def get_top_products():
    """Return the 10 best-selling products."""
    df = conn.query(
        """
        SELECT
            product_name,
            SUM(sales)    AS sales,
            SUM(profit)   AS profit,
            SUM(quantity) AS quantity
        FROM orders
        GROUP BY product_name
        ORDER BY sales DESC
        LIMIT 10;
        """,
        ttl=0,
    )
    df[["sales", "profit"]] = df[["sales", "profit"]].astype(float)
    return df


# ---------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------
def pct_change(series) -> str:
    """Percent change between the last two months."""
    last, prev = float(series.iloc[-1]), float(series.iloc[-2])
    return f"{(last - prev) / prev:.1%}" if prev else "0%"


def points_change(series) -> str:
    """Difference in percentage points between the last two months."""
    diff = (float(series.iloc[-1]) - float(series.iloc[-2])) * 100
    return f"{diff:+.1f} pts"


def spark(series) -> list[float]:
    """Convert a series to a list of floats for the chart."""
    return series.astype(float).tolist()


# ---------------------------------------------------------------
# Data
# ---------------------------------------------------------------
kpi = get_kpis()
monthly = get_monthly()

avg_basket = float(kpi["total_sales"]) / float(kpi["total_orders"])
margin = float(kpi["total_profit"]) / float(kpi["total_sales"])

DELTA_HELP = "Delta = variation between the last two months of data."

# ---------------------------------------------------------------
# KPIs
# ---------------------------------------------------------------
st.subheader("Key Performance Indicators")

# Row 1
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Total orders",
        f"{int(kpi['total_orders']):,}",
        delta=pct_change(monthly["orders"]),
        chart_data=spark(monthly["orders"]),
        chart_type="line",
        icon=":material/shopping_cart:",
        border=True,
        help=DELTA_HELP,
    )

with col2:
    st.metric(
        "Total sales",
        f"${float(kpi['total_sales']):,.0f}",
        delta=pct_change(monthly["sales"]),
        chart_data=spark(monthly["sales"]),
        chart_type="area",
        icon=":material/payments:",
        border=True,
        help=DELTA_HELP,
    )

with col3:
    st.metric(
        "Total profit",
        f"${float(kpi['total_profit']):,.0f}",
        delta=pct_change(monthly["profit"]),
        chart_data=spark(monthly["profit"]),
        chart_type="bar",
        icon=":material/trending_up:",
        border=True,
        help=DELTA_HELP,
    )

# Row 2
col4, col5, col6 = st.columns(3)

with col4:
    st.metric(
        "Customers",
        f"{int(kpi['total_customers']):,}",
        delta=pct_change(monthly["customers"]),
        chart_data=spark(monthly["customers"]),
        chart_type="line",
        icon=":material/group:",
        border=True,
        help=DELTA_HELP,
    )

with col5:
    st.metric(
        "Average basket",
        f"${avg_basket:,.2f}",
        delta=pct_change(monthly["avg_basket"]),
        chart_data=spark(monthly["avg_basket"]),
        chart_type="line",
        icon=":material/receipt_long:",
        border=True,
        help=DELTA_HELP,
    )

with col6:
    st.metric(
        "Profit margin",
        f"{margin:.1%}",
        delta=points_change(monthly["margin"]),
        chart_data=spark(monthly["margin"]),
        chart_type="area",
        icon=":material/percent:",
        border=True,
        help=DELTA_HELP,
    )

# ---------------------------------------------------------------
# Section 1: Monthly trend
# ---------------------------------------------------------------
st.divider()
st.subheader("Monthly trend")

metric_choice = st.segmented_control(
    "Metric",
    options=["sales", "profit", "orders"],
    default="sales",
    format_func=str.capitalize,
)

st.line_chart(
    monthly.set_index("month")[[metric_choice or "sales"]],
    height=350,
)

# ---------------------------------------------------------------
# Section 2: Performance breakdown
# ---------------------------------------------------------------
st.divider()
st.subheader("Performance breakdown")

left, right = st.columns(2)

with left:
    st.markdown("**Sales and profit by region**")
    by_region = get_by_region()
    st.bar_chart(by_region.set_index("region")[["sales", "profit"]])

with right:
    st.markdown("**Top 10 products by sales**")
    st.dataframe(
        get_top_products(),
        hide_index=True,
        column_config={
            "product_name": "Product",
            "sales": st.column_config.NumberColumn("Sales", format="$%.0f"),
            "profit": st.column_config.NumberColumn("Profit", format="$%.0f"),
            "quantity": st.column_config.NumberColumn("Qty"),
        },
    )