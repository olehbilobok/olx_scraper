import os
import threading
from urllib.parse import urlparse

import schedule
import time
from datetime import datetime

from config import DUMP_PATH
from scraper import scrape_olx
from database import Session
from logger import logger


def dump_database():
    try:
        # Get the database URL from the SQLAlchemy session (db_url format: postgresql+psycopg2://user:password@localhost/dbname)
        db_url = Session().get_bind().url
        parsed_url = urlparse(str(db_url))

        # Extract connection details from the parsed URL
        user = parsed_url.username
        password = parsed_url.password
        host = parsed_url.hostname
        port = parsed_url.port
        database = parsed_url.path[1:]  # Remove the leading '/' from the database name

        # Create the timestamped dump file name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dump_file = f"{DUMP_PATH}/db_dump_{timestamp}.sql"

        logger.info(f"Dumping database to {dump_file}")

        # Form the pg_dump command
        command = f"pg_dump --host={host} --port={port} --username={user} --dbname={database} --no-password --file={dump_file}"

        # Set the PGPASSWORD environment variable to avoid interactive password prompt
        os.environ["PGPASSWORD"] = password

        # Execute the pg_dump command
        os.system(command)
        logger.info(f"Dump database is finished")
    except Exception as ex:
        logger.error(f"Error while dump database")
        return


def start_scheduler():
    logger.info("Starting scheduler...")

    # Define a function to run tasks in a separate thread
    def run_in_thread(func, *args):
        thread = threading.Thread(target=func, args=args)
        thread.start()

    # Schedule tasks
    schedule.every(1).minutes.do(lambda: run_in_thread(scrape_olx, Session))
    schedule.every(1).day.at("12:00").do(lambda: run_in_thread(dump_database))

    # Run the scheduler
    while True:
        schedule.run_pending()
        time.sleep(1)
