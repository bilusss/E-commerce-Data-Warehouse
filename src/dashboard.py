import streamlit as st
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
col1, col2, col3 = st.columns(3)
col4, col5 = st.columns(2)

total_revenue = pd.read_sql("""
  SELECT ROUND(SUM(revenue)::numeric, 2) FROM fact_orders
""", engine)
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


col1.metric("💰 Total revenue", f"R$ {total_revenue.iloc[0,0]:,}")
col2.metric("📊 Total orders", f" {total_orders.iloc[0,0]}")
col3.metric("🏷️ Average order value", f"R$ {avg_order_value.iloc[0,0]:,.2f}")
col4.metric("⭐️ Average customer satisfaction", f"{review_score.iloc[0,0]:.2f}")
col5.metric("📦 Orders being late", f"{order_estimated_delivery_date.iloc[0,0]:.2f} %")

# --- Sprzedaż miesięczna ---


# --- Top kategorie ---


# --- Tabela stanów ---


# --- Schema explorer ---
with st.expander("🔍 Schema explorer", expanded=False):
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
