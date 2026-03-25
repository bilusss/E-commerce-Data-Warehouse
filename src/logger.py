import logging
import os
from datetime import datetime

def get_logger(name: str) -> logging.Logger:
  logger = logging.getLogger(name)

  if logger.handlers:
    return logger
  
  logger.setLevel(logging.DEBUG)
  
  formatter = logging.Formatter(
    "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
  )
  
  # Console - only INFO and upper
  console_handler = logging.StreamHandler()
  console_handler.setLevel(logging.INFO)
  console_handler.setFormatter(formatter)
  
  # Files - everything and date in filename
  os.makedirs("logs", exist_ok=True)
  log_file = f"logs/etl_{datetime.now().strftime('%Y%m%d')}.log"
  file_handler = logging.FileHandler(log_file, encoding="utf-8")
  file_handler.setLevel(logging.DEBUG)
  file_handler.setFormatter(formatter)
  
  logger.addHandler(console_handler)
  logger.addHandler(file_handler)

  return logger