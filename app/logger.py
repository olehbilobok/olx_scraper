import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from config import LOG_DIR

os.makedirs(LOG_DIR, exist_ok=True)

def setup_logger():
    logger = logging.getLogger("olx_scraper")
    logger.setLevel(logging.INFO)
    # File handler
    handler = RotatingFileHandler(
        os.path.join(LOG_DIR, "scraper.log"), maxBytes=1024 * 1024 * 1024, backupCount=5
    )
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    logger.addHandler(handler)
    logger.addHandler(console_handler)
    return logger

logger = setup_logger()