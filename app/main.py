from scheduler import start_scheduler
from logger import logger


if __name__ == "__main__":
    logger.info("Starting OLX scraper...")
    start_scheduler()