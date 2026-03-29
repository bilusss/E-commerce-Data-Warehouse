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

  """
  Data types handling
  """
  logger.info("Started changing data types for pandas-like")

  logger.debug("Changing data types - customers")
  customers["customer_zip_code_prefix"] = customers["customer_zip_code_prefix"].astype(pd.Int64Dtype())
  
  logger.debug("Changing data types - geolocation")
  geolocation["geolocation_zip_code_prefix"] = geolocation["geolocation_zip_code_prefix"].astype(pd.Int32Dtype())
  geolocation["geolocation_lat"] = geolocation["geolocation_lat"].astype(pd.Float64Dtype())
  geolocation["geolocation_lng"] = geolocation["geolocation_lng"].astype(pd.Float64Dtype())

  logger.debug("Changing data types - order_items")
  order_items["order_item_id"] = order_items["order_item_id"].astype(pd.Int64Dtype())
  order_items["shipping_limit_date"] = pd.to_datetime(order_items["shipping_limit_date"], errors="coerce")
  order_items["price"] = order_items["price"].astype(pd.Float64Dtype())
  order_items["freight_value"] = order_items["freight_value"].astype(pd.Float64Dtype())

  logger.debug("Changing data types - payments")
  payments["payment_sequential"] = payments["payment_sequential"].astype(pd.Int8Dtype())
  payments["payment_installments"] = payments["payment_installments"].astype(pd.Int16Dtype())
  payments["payment_value"] = payments["payment_value"].astype(pd.Float64Dtype())

  logger.debug("Changing data types - reviews")
  reviews["review_score"] = reviews["review_score"].astype(pd.Int8Dtype())
  reviews["review_creation_date"] = pd.to_datetime(reviews["review_creation_date"], errors="coerce")
  reviews["review_answer_timestamp"] = pd.to_datetime(reviews["review_answer_timestamp"], errors="coerce")

  logger.debug("Changing data types - orders")
  date_cols = ["order_purchase_timestamp", "order_approved_at", "order_delivered_carrier_date",
                        "order_delivered_customer_date", "order_estimated_delivery_date"]
  for col in date_cols:
    orders[col] = pd.to_datetime(orders[col], errors="coerce")

  logger.debug("Changing data types - products")
  products["product_photos_qty"] = products["product_photos_qty"].astype(pd.Int16Dtype())
  float_cols = ["product_name_lenght",
       "product_description_lenght", "product_weight_g",
       "product_length_cm", "product_height_cm", "product_width_cm"]
  
  for col in float_cols:
    products[col] = products[col].astype(pd.Float64Dtype())

  logger.debug("Changing data types - sellers")
  sellers["seller_zip_code_prefix"] = sellers["seller_zip_code_prefix"].astype(pd.Int64Dtype())

  """
  Feature engieneering
  """
  logger.info(f"Started feature engineering")

  logger.debug("Feature engineering - reviews")
  reviews["response_time_days"] = (reviews["review_answer_timestamp"] - reviews["review_creation_date"]).dt.days
  reviews["sentiment"] = pd.cut(reviews["review_score"], bins=[0, 2, 3, 5], labels=["negative", "neutral", "positive"])

  logger.debug("Feature engineering - orders")
  orders["delivery_days"] = (orders["order_delivered_customer_date"] - orders["order_purchase_timestamp"]).dt.days
  orders["delay_days"] = (orders["order_delivered_customer_date"] - orders["order_estimated_delivery_date"]).dt.days
  orders["purchase_hour"] = orders["order_purchase_timestamp"].dt.hour
  orders["purchase_dow"]  = orders["order_purchase_timestamp"].dt.day_name()
  orders["day_part"] = pd.cut(orders["purchase_hour"], bins=[0, 6, 12, 18, 24],
                          labels=["night", "morning", "afternoon", "evening"],right=False)
  
  logger.debug("Feature engineering - order_items")
  order_items["revenue"] = order_items["price"] + order_items["freight_value"]
  # freight value = transport cost


  logger.debug(f"Started aggregation")
  payment_agg = payments.groupby("order_id").agg(total_payment=("payment_value", "sum"),
                          payment_installments=("payment_installments", "max"), payment_type=("payment_type", "first")).reset_index()

  geo_agg = (geolocation.groupby("geolocation_zip_code_prefix")[["geolocation_lat", "geolocation_lng"]].mean().reset_index())


  logger.info(f"Started creating star schema")
  logger.debug(f"Started creating fact table")
  fact_orders = (
    orders[["order_id", "customer_id", "order_status", "order_purchase_timestamp", "delivery_days", "delay_days",
            "purchase_hour", "purchase_dow", "day_part"]]
    .merge(
        order_items[["order_id", "product_id", "seller_id", "price", "freight_value", "revenue"]], on="order_id", how="left"
    )
    .merge(payment_agg, on="order_id", how="left")
  )

  logger.debug(f"Started creating dimensional tables")
  dim_customer = (
    customers[["customer_id", "customer_unique_id", "customer_city", "customer_state", "customer_zip_code_prefix"]]
    .drop_duplicates()
    .merge(geo_agg, left_on="customer_zip_code_prefix", right_on="geolocation_zip_code_prefix", how="left")
    .drop(columns="geolocation_zip_code_prefix")
  )

  dim_seller = (
    sellers[["seller_id", "seller_city", "seller_state", "seller_zip_code_prefix"]]
    .drop_duplicates()
    .merge(geo_agg, left_on="seller_zip_code_prefix", right_on="geolocation_zip_code_prefix", how="left")
    .drop(columns="geolocation_zip_code_prefix")
  )

  dim_product = (
    products.merge(category_names, on="product_category_name", how="left")
    .assign(category_en=lambda x: x["product_category_name_english"].fillna("unknown"))
  )[["product_id", "category_en", "product_weight_g", "product_length_cm", "product_height_cm", "product_width_cm",
    "product_photos_qty"]].drop_duplicates()

  dim_date = (
    orders[["order_purchase_timestamp", "purchase_hour", "purchase_dow", "day_part"]]
    .drop_duplicates(subset=["order_purchase_timestamp"])
    .assign(
        year=lambda x: x["order_purchase_timestamp"].dt.year,
        month=lambda x: x["order_purchase_timestamp"].dt.month,
        day=lambda x: x["order_purchase_timestamp"].dt.day,
    )
    .rename(columns={"order_purchase_timestamp": "date"})
  )

  dim_review = reviews[["review_id", "order_id", "review_score", "sentiment", "response_time_days"]].drop_duplicates()

  logger.info(f"Completed doing 1 fact table and 5 dimension tables")
  return {
    "fact_orders":   fact_orders,
    "dim_customer":  dim_customer,
    "dim_product":   dim_product,
    "dim_seller":    dim_seller,
    "dim_date":      dim_date,
    "dim_review":    dim_review,
  }