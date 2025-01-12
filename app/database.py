from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from models import Base
from config import DATABASE_URL
from logger import logger
from sqlalchemy_utils import database_exists, create_database


def init_db():
    """
        Initialize the database:
        - Creates the database if it does not exist.
        - Sets up tables based on the SQLAlchemy ORM models.
        - Returns a sessionmaker instance for database interactions.
    """
    try:
        engine = create_engine(DATABASE_URL)

        if not database_exists(engine.url):
            create_database(engine.url)
            logger.info(f"Database created at {engine.url}")

        Base.metadata.create_all(engine)
        logger.info("Database tables created or already exist.")
        return sessionmaker(bind=engine)
    except SQLAlchemyError as ex:
        logger.error(f"Error initializing the database: {ex}")
        raise

Session= init_db()
