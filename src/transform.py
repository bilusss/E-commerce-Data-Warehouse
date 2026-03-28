import pandas as pd
from logger import get_logger

logger = get_logger("transform")

def transform(dfs: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
  customers       = dfs["customers"].copy()
  geolocation     = dfs["geolocation"].copy()
  order_items     = dfs["order_items"].copy()
  payments        = dfs["payments"].copy()
  reviews         = dfs["reviews"].copy()
  orders          = dfs["orders"].copy()
  products        = dfs["products"].copy()
  sellers         = dfs["sellers"].copy()
  category_names  = dfs["category_names"].copy()

  # print("=== CUSTOMERS ===")
  customers["customer_zip_code_prefix"] = customers["customer_zip_code_prefix"].astype(pd.Int64Dtype())

  # NaN handling
  # print(customers.isnull().mean() * 100)
  # print(customers["order_status"].value_counts())
  print(customers.info())
  with pd.option_context('display.max_columns', None):
    print(customers.sample(n=5))
  
  # print("\n=== GEOLOCATION ===")
  geolocation["geolocation_zip_code_prefix"] = geolocation["geolocation_zip_code_prefix"].astype(pd.Int32Dtype())
  geolocation["geolocation_lat"] = geolocation["geolocation_lat"].astype(pd.Float64Dtype())
  geolocation["geolocation_lng"] = geolocation["geolocation_lng"].astype(pd.Float64Dtype())

  # print("\n=== ORDER_ITEMS ===")
  order_items["order_item_id"] = order_items["order_item_id"].astype(pd.Int64Dtype())
  order_items["shipping_limit_date"] = pd.to_datetime(order_items["shipping_limit_date"], errors="coerce")
  order_items["price"] = order_items["price"].astype(pd.Float64Dtype())
  order_items["freight_value"] = order_items["freight_value"].astype(pd.Float64Dtype())

  # print("\n=== PAYMENTS ===")
  payments["payment_sequential"] = payments["payment_sequential"].astype(pd.Int8Dtype())
  payments["payment_installments"] = payments["payment_installments"].astype(pd.Int64Dtype())
  payments["payment_value"] = payments["payment_value"].astype(pd.Float64Dtype())

  # print("\n=== REVIEWS ===")
  reviews["review_score"] = reviews["review_score"].astype(pd.Int8Dtype())
  reviews["review_creation_date"] = pd.to_datetime(reviews["review_creation_date"], errors="coerce")
  reviews["review_answer_timestamp"] = pd.to_datetime(reviews["review_answer_timestamp"], errors="coerce")

  # print("\n=== ORDERS ===")
  date_cols = ["order_purchase_timestamp", "order_approved_at", "order_delivered_carrier_date",
                        "order_delivered_customer_date", "order_estimated_delivery_date"]
  for col in date_cols:
    orders[col] = pd.to_datetime(orders[col], errors="coerce")

  # print("\n=== PRODUCTS ===")
  float_cols = ["product_name_lenght",
       "product_description_lenght", "product_photos_qty", "product_weight_g",
       "product_length_cm", "product_height_cm", "product_width_cm"]
  
  for col in float_cols:
    products[col] = products[col].astype(pd.Float64Dtype())

  # print("\n=== SELLERS ===")
  sellers["seller_zip_code_prefix"] = sellers["seller_zip_code_prefix"].astype(pd.Int64Dtype())

  # print("\n=== CATEGORY_NAMES ===")
  

  
  return dfs
