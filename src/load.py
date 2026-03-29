import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
from logger import get_logger

logger = get_logger("load")
load_dotenv()
DB_URL = os.getenv("DB_URL", "postgresql://admin:admin@localhost:5433/br_e_commerce_dwh")

TABLE_ORDER = [
  "dim_customer",
  "dim_product",
  "dim_seller",
  "dim_date",
  "dim_review",
  "fact_orders"
]

def load(tables: dict[str, pd.DataFrame]) -> None:
  engine = create_engine(DB_URL)
  logger.info("Connected to database")

  for table_name in TABLE_ORDER:
    df = tables[table_name]
    df.to_sql(
      name=table_name,
      con=engine,
      if_exists="replace",
      index=False,
      method="multi",
      chunksize=1000
    )
    logger.info(f"Loaded {table_name} — {len(df)} rows")

  logger.info("Load complete")