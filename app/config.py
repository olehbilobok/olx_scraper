import os


SCRAPE_URL = 'https://www.olx.ua/uk/list/'
PRODUCT_URL_PREFIX = 'https://www.olx.ua'
PAGES = 5
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql+psycopg2://postgres:postgres@localhost:5432/olx_scraper_db')
DUMP_PATH = os.path.join(os.path.dirname(__file__), '..', 'dumps')
LOG_DIR = os.path.join(os.path.dirname(__file__), '..', 'logs')