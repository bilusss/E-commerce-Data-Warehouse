import pandas as pd
from logger import get_logger

def transform(dfs: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
  customers       = dfs["orders"].copy()
  geolocation     = dfs["geolocation"].copy()
  order_items     = dfs["order_items"].copy()
  payments        = dfs["payments"].copy()
  reviews         = dfs["reviews"].copy()
  orders          = dfs["orders"].copy()
  products        = dfs["products"].copy()
  sellers         = dfs["sellers"].copy()
  category_names  = dfs["category_names"].copy()

  # Cleaning data

  # date conversion

  date_cols = []



  print("=== CUSTOMERS ===")
  print(customers.info())
  print(customers.head())

  print("\n=== GEOLOCATION ===")
  print(geolocation.info())
  print(geolocation.head())

  print("\n=== ORDER_ITEMS ===")
  print(order_items.info())
  print(order_items.head())

  print("\n=== PAYMENTS ===")
  print(payments.info())
  print(payments.head())

  print("\n=== REVIEWS ===")
  print(reviews.info())
  print(reviews.head())

  print("\n=== ORDERS ===")
  print(orders.info())
  print(orders.head())

  print("\n=== PRODUCTS ===")
  print(products.info())
  print(products.head())

  print("\n=== SELLERS ===")
  print(sellers.info())
  print(sellers.head())

  print("\n=== CATEGORY_NAMES ===")
  print(category_names.info())
  print(category_names.head())

  return dfs
