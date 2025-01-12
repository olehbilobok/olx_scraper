import threading
import uuid

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

from logger import logger
from config import PAGES, SCRAPE_URL, PRODUCT_URL_PREFIX
from models import User, Goods, Image, PhoneNumber, Category


def fetch_page(url):
    """Fetch the content of a page."""
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            logger.error(f"Failed to fetch {url} (Status Code: {response.status_code})")
    except Exception as e:
        logger.error(f"Error fetching {url}: {e}")

def get_all_products(page_content):
    """Extract all products from the page content."""
    soup = BeautifulSoup(page_content, 'html.parser')
    try:
        products = soup.find_all('div', class_='css-u2ayx9')
        return products
    except AttributeError:
        logger.warning("Products not found")
        return []

def get_product_url(product):
    """Extract product URL from the listing."""
    try:
        product_url = product.find('a', class_='css-qo0cxu').get('href')
        return f"{PRODUCT_URL_PREFIX}{product_url}"
    except AttributeError:
        logger.warning("Product URL not found in list")
        return None

def extract_product_details(product_url):
    """Extract details from a product page."""
    content = fetch_page(product_url)
    if not content:
        return None

    soup = BeautifulSoup(content, 'html.parser')

    def safe_find(selector, attr='text', default=None):
        """Helper function to safely extract elements."""
        try:
            element = soup.select_one(selector)
            return getattr(element, attr) if element else default
        except Exception:
            return default

    ad_id = safe_find('span.css-12hdxwj', default="")
    parsed_data = {
        "id": int(ad_id.split()[-1]) if ad_id else uuid.uuid4().hex[:9],
        "title": safe_find('h4.css-1kc83jo'),
        "publication_date": clean_date(safe_find('span.css-19yf5ek')),
        "price": clean_price(safe_find('h3.css-90xrc0')),
        "description": safe_find('div.css-1o924a9'),
        "views": safe_find('span.css-42xwsi'),
        "product_url": product_url,
        "user_name": safe_find('h4.css-1lcz6o7'),
        "rating": safe_find('p.css-9pgvpt'),
        "registration_date": clean_date(safe_find('p.css-23d1vy')),
        "last_seen": clean_date(safe_find('span.css-1p85e15')),
        "location": safe_find('div.css-13l8eec p.css-1cju8pu'),
        "phone": safe_find('p.css-7twvcr'),
        "categories": [cat.text for cat in soup.select('ul.css-rn93um p.css-b5m1rv')],
        "image_urls": [
            img.get('src') for img in soup.select('div.swiper-zoom-container img')
        ],
    }
    return parsed_data


def clean_price(data_string):
    try:
        return int(data_string.split()[0]) if data_string else None
    except Exception as ex:
        return 0


def clean_date(date_string):
    # Mapping Russian month names to their numerical values
    if not date_string:
        return datetime.now()

    months = {
        # Russian months
        "январь": 1, "января": 1,
        "февраль": 2, "февраля": 2,
        "март": 3, "марта": 3,
        "апрель": 4, "апреля": 4,
        "май": 5, "мая": 5,
        "июнь": 6, "июня": 6,
        "июль": 7, "июля": 7,
        "август": 8, "августа": 8,
        "сентябрь": 9, "сентября": 9,
        "октябрь": 10, "октября": 10,
        "ноябрь": 11, "ноября": 11,
        "декабрь": 12, "декабря": 12,

        # Ukrainian months
        "січень": 1, "січня": 1,
        "лютий": 2, "лютого": 2,
        "березень": 3, "березня": 3,
        "квітень": 4, "квітня": 4,
        "травень": 5, "травня": 5,
        "червень": 6, "червня": 6,
        "липень": 7, "липня": 7,
        "серпень": 8, "серпня": 8,
        "вересень": 9, "вересня": 9,
        "жовтень": 10, "жовтня": 10,
        "листопад": 11, "листопада": 11,
        "грудень": 12, "грудня": 12,
    }

    try:
        # Clean the string by removing common prefixes
        if "Онлайн" in date_string.split():
            if "вчера" in date_string.split():
                yesterday = datetime.now() - timedelta(days=1)
                time_str = date_string.split()[-1]
                hours, minutes = map(int, time_str.split(':'))
                # Create a new datetime object with yesterday's date and the specified time
                return yesterday.replace(hour=hours, minute=minutes, second=0, microsecond=0)
            elif "в" in date_string.split():
                time_str = date_string.split()[-1]
                hours, minutes = map(int, time_str.split(':'))
                today = datetime.now()
                return today.replace(hour=hours, minute=minutes, second=0, microsecond=0)
            else:
                date_string = date_string.replace("Онлайн", "").strip()  # Case: "Онлайн"
        elif "Сегодня" or "Сьогодні" in date_string.split():
            time_str = date_string.split()[-1]
            hours, minutes = map(int, time_str.split(':'))
            today = datetime.now()
            return today.replace(hour=hours, minute=minutes, second=0, microsecond=0)

        elif "на OLX с" or "на OLX з" in date_string:
            date_string = date_string.replace("на OLX с", "").strip()  # Case: "на OLX с"

        # Split and clean the date components
        parts = date_string.split()  # Example: ["10", "января", "2025"] or ["декабрь", "2019"]

        # Handle "Онлайн" format ("10 января 2025")
        if len(parts) == 4:
            day = int(parts[0])  # First part is the day
            month_name = parts[1].lower()  # Second part is the month name
            month = months[month_name]  # Map the month name to a number
            year = int(parts[2])  # Third part is the year
            return datetime(year, month, day)

        # Handle "на OLX с" format ("декабрь 2019")
        elif len(parts) == 3:
            month_name = parts[0].lower()  # First part is the month name
            month = months[month_name]  # Map the month name to a number
            year = int(parts[1])  # Second part is the year
            return datetime(year, month, 1)  # Default to the 1st day of the month

        # If the format doesn't match the expected structure
        else:
            raise ValueError("Date string format is incorrect.")

    except (ValueError, KeyError, IndexError) as e:
        # Log and handle errors gracefully
        print(f"Error parsing date: {date_string} -> {e}")
        return


def save_data_to_db(session, product_details):
    """Save data to the database."""
    try:
        user = session.query(User).filter_by(name=product_details["user_name"]).first()
        if not user:
            user = User(
                name=product_details["user_name"],
                rating=float(product_details["rating"]) if product_details["rating"] else None,
                registration_date=product_details["registration_date"],
                last_seen=product_details["last_seen"],
                location=product_details["location"]
            )
            session.add(user)

        phone_number = product_details.get("phone")
        if phone_number and 'xxx' not in phone_number:
            phone_number = PhoneNumber(number=product_details["phone"], user=user)
            session.add(phone_number)

        # Check if the product already exists based on its ID
        existing_product = session.query(Goods).filter_by(id=product_details["id"]).first()
        if existing_product:
            logger.info(f"Product with ID {product_details['id']} already exists in the database.")
            return

        new_product = Goods(
            id=product_details["id"],
            title=product_details["title"],
            publication_date=product_details["publication_date"],
            price=product_details["price"],
            description=product_details["description"],
            views=product_details["views"],
            url=product_details["product_url"],
            user=user
        )
        session.add(new_product)

        for category_name in product_details["categories"]:
            category = Category(name=category_name, goods=new_product)
            session.add(category)

            # Save images
        for image_url in product_details["image_urls"]:
            image = Image(url=image_url, goods=new_product)
            session.add(image)

        session.commit()
        logger.info(f"Product {product_details['title']} (ID: {product_details['id']}) saved to the database.")
    except Exception as e:
        session.rollback()
        logger.error(f"Error saving product to the database: {e}")


def process_page(url, session):
    """Process a single page of products."""
    session = session()
    page_content = fetch_page(url)

    if not page_content:
        logger.warning(f"Failed to fetch content for {url}")
        return

    products = get_all_products(page_content)

    for product in products:
        product_url = get_product_url(product)
        if not product_url:
            continue

        product_details = extract_product_details(product_url)
        if product_details:
            logger.info(f"Scraped product: {product_details['title']} (ID: {product_details['id']})")
            with session:
                save_data_to_db(session, product_details)


def scrape_olx(session):
    """Main scraping function."""
    threads = []
    for page in range(1, PAGES + 1):  # Consider scraping multiple pages
        url = f"{SCRAPE_URL}?page={page}"
        logger.info(f"Scraping {url}")
        thread = threading.Thread(target=process_page, args=(url, session))
        threads.append(thread)
        thread.start()

    # Wait for all threads to finish
    for thread in threads:
        thread.join()

    logger.info("Data scraped")
