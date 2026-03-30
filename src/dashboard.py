import streamlit as st
import plotly.express as px
import pandas as pd
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv()
engine = create_engine(os.getenv("DB_URL", "postgresql://admin:admin@localhost:5433/br_e_commerce_dwh"))

st.set_page_config(page_title="E-commerce DWH", layout="wide")
st.title("🛒 E-commerce Data Warehouse Dashboard")

# --- KPI ---
# (Key Performance Indicators)

total_revenue = pd.read_sql("""
  SELECT ROUND(SUM(revenue)::numeric, 2) FROM fact_orders
""", engine)

last_30d_revenue = pd.read_sql("""
    SELECT ROUND(SUM(revenue)::numeric, 2) AS revenue
    FROM fact_orders
    WHERE order_purchase_timestamp >= NOW() - INTERVAL '30 days'
""", engine)

prev_30d_revenue = pd.read_sql("""
    SELECT ROUND(SUM(revenue)::numeric, 2) AS revenue
    FROM fact_orders
    WHERE order_purchase_timestamp >= NOW() - INTERVAL '60 days'
      AND order_purchase_timestamp  < NOW() - INTERVAL '30 days'
""", engine)

current  = last_30d_revenue.iloc[0, 0] or 0
previous = prev_30d_revenue.iloc[0, 0] or 0

if previous == 0:
    delta_str = "no data for previous period"
else:
    delta = round((current - previous) * 100 / previous, 1)
    delta_str = f"{delta:+.1f}% vs previous 30d"

col1,col2 = st.columns(2)
col1.metric("💰 Total revenue", f"R$ {total_revenue.iloc[0,0]:,}")
col2.metric("📅 Last 30 days revenue", f"R$ {current:,}", delta=delta_str)

st.divider()

col1, col2, col3, col4 = st.columns(4)

total_orders = pd.read_sql("""
  SELECT COUNT(DISTINCT(order_id)) FROM fact_orders
""", engine)
avg_order_value = pd.read_sql("""
  SELECT SUM(revenue) / COUNT(DISTINCT order_id) FROM fact_orders
""", engine)
review_score = pd.read_sql("""
  SELECT AVG(review_score) FROM dim_review
""", engine)
order_estimated_delivery_date = pd.read_sql("""
  SELECT 
    SUM(
      CASE
        WHEN delay_days > 0
        THEN 1
        ELSE 0
      END
    ) * 100.0 / COUNT(*)
FROM fact_orders
WHERE delay_days IS NOT NULL;
""", engine)


col1.metric("📊 Total orders", f" {total_orders.iloc[0,0]}")
col2.metric("🏷️ Average order value", f"R$ {avg_order_value.iloc[0,0]:,.2f}")
col3.metric("⭐️ Average customer satisfaction", f"{review_score.iloc[0,0]:.2f}")
col4.metric("📦 Orders being late", f"{order_estimated_delivery_date.iloc[0,0]:.2f} %")

# --- Monthly performance ---
st.subheader("📈 Monthly Revenue")

monthly = pd.read_sql("""
SELECT
  d.year,
  d.month,
  ROUND(SUM(f.revenue)::numeric, 2) AS revenue
FROM fact_orders f
JOIN dim_date d
  ON d.date = f.order_purchase_timestamp
GROUP BY d.year, d.month
ORDER BY d.year ASC, d.month ASC
""", engine)

monthly["period"] = monthly["year"].astype(str) + "-" + monthly["month"].astype(str).str.zfill(2)
# zfill to make sure order by ASC works correctly - otherwise 1, 10, 11, 2,...

dates = pd.date_range(start=monthly["period"].iloc[0], end=monthly["period"].iloc[-1], freq='MS').strftime('%Y-%m')
dates = pd.DataFrame({"period": dates})

monthly.drop(columns=["year", "month"], inplace=True)
monthly = pd.merge(left=dates, right=monthly, how="left", on="period")
monthly["revenue"].fillna(value=0 ,inplace=True)
monthly = monthly.iloc[:-1]

st.line_chart(monthly, x="period", y="revenue", color="blue", x_label="Period", y_label="Revenue")

# --- Top categories ---
st.subheader("🏆 Top 10 Product Categories")
st.info("Based on Revenue", icon="ℹ️")
print("="*30)
print("="*30)

top_categories = pd.read_sql("""
SELECT
  d.category_en,
  ROUND(SUM(f.revenue)::numeric, 2) AS total_revenue
FROM fact_orders f
JOIN dim_product d
  ON f.product_id = d.product_id
GROUP BY
  d.category_en
ORDER BY
  SUM(f.revenue) DESC
LIMIT 10
""", engine)

# streamlit sorts automatically based on x-axis which looks not natural so that i'll use plotly that respects the x indexes
# st.bar_chart(top_categories, x="category_en", y="total_revenue", color="#9F11A2", x_label="🗃️ CATEGORY 🗃️", y_label="💸 REVENUE 💸", horizontal=True)

fig = px.bar(top_categories, x="total_revenue", y="category_en", orientation="h",
             labels={"total_revenue": "Revenue", "category_en": "Category"})
fig.update_layout(yaxis={"categoryorder": "total ascending"})
st.plotly_chart(fig, width='stretch')

# --- Revenue by Customer State ---
st.subheader("🗺️ Revenue by Customer State")
st.info("Only Top 15 States", icon="ℹ️")

by_state = pd.read_sql("""
SELECT 
  d.customer_state,
  COUNT(DISTINCT(f.order_id)) AS total_orders,
  ROUND(SUM(f.revenue)::numeric, 2) AS total_revenue
FROM
  fact_orders f
INNER JOIN dim_customer d
  ON f.customer_id = d.customer_id
WHERE
  d.customer_state IS NOT NULL 
GROUP BY
  d.customer_state
ORDER BY
  SUM(f.revenue) DESC
LIMIT 15
""", engine)

# Done inner join as i want to get rid off NaNs

by_state_chart = px.pie(by_state, names="customer_state", values="total_revenue")
st.plotly_chart(by_state_chart, width='stretch')

# --- Schema explorer ---
st.subheader("🔍 Schema explorer")
with st.expander("",expanded=False):
# with st.expander("",expanded=True):
  schema = pd.read_sql("""
    SELECT table_name, column_name, data_type
    FROM information_schema.columns
    WHERE table_schema = 'public'
    ORDER BY table_name, ordinal_position
  """, engine)

  for table in schema["table_name"].unique():
    cols = schema[schema["table_name"] == table][["column_name", "data_type"]]
    st.markdown(f"**{table}**")
    st.dataframe(cols, hide_index=True, width="stretch")
