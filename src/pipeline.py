from extract import extract
from transform import transform
from load import load
from logger import get_logger
import pandas as pd
import time

logger = get_logger("pipeline")

def run_pipeline():
  try:
    logger.info(f"Started running pipeline cycle")

    start = time.perf_counter()

    logger.info("Step 1/3: extract")
    raw = extract()

    logger.info("Step 2/3: transform")
    transformed = transform(raw)
    
    logger.info("Step 3/3: load")
    load(transformed)

    logger.info(f"Pipeline finished in {time.perf_counter() - start}s")

  except Exception as e:
    logger.exception(f"Failed running pipeline - {e}")
  return


if __name__ == "__main__":
  logger.info("="*30)
  logger.info(f"ETL Pipeline start")
  
  
  run_pipeline()

  logger.info(f"Pipeline complete")
