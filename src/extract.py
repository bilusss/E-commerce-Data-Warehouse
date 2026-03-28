import kagglehub
import os
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
from logger import get_logger

logger = get_logger("extract")

load_dotenv()
DATASET_HANDLE = os.getenv("LINK_TO_DATASET") or "olistbr/brazilian-ecommerce"

RAW_DIR = Path("data/raw")

def download_dataset() -> bool:
  try:
    logger.info(f"Downloading dataset: {DATASET_HANDLE}")
    dataset_dir = kagglehub.dataset_download(DATASET_HANDLE, output_dir=str(RAW_DIR))
    logger.info(f"Dataset downloaded to: {dataset_dir}")
    return True
  except Exception as e:
    logger.exception(f"Error downloading dataset: {e}")
    return False

def extract() -> dict[str, pd.DataFrame]:
  files = {
    "customers":      "olist_customers_dataset.csv",
    "geolocation":    "olist_geolocation_dataset.csv",
    "order_items":    "olist_order_items_dataset.csv",
    "payments":       "olist_order_payments_dataset.csv",
    "reviews":        "olist_order_reviews_dataset.csv",
    "orders":         "olist_orders_dataset.csv",
    "products":       "olist_products_dataset.csv",
    "sellers":        "olist_sellers_dataset.csv",
    "category_names": "product_category_name_translation.csv"
  }

  dataframes = {}
  for name, filename in files.items():
    try:
      path = RAW_DIR / filename
      dataframes[name] = pd.read_csv(path)
      logger.info(f"Loaded {name}: {len(dataframes[name])} rows")
    except FileNotFoundError:
      logger.warning(f"File not found: {path} - Attempting to download dataset")
      if download_dataset():
        dataframes[name] = pd.read_csv(path)
        logger.info(f"Loaded {name}: {len(dataframes[name])} rows")
      else:
        logger.error(f"Failed to download dataset and load {name}")
        raise
    except Exception as e:
      logger.exception(f"Error loading {name} from {path}: {e}")
      raise
  return dataframes

if __name__ == "__main__":
  try:
    data = extract()
    logger.info(f"Successfully extracted {len(data)} datasets")
  except Exception as e:
    logger.error(f"Extraction failed: {e}")