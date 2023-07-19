from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base
from sqlalchemy.engine import URL
from dotenv import load_dotenv
import os


def _init():
    load_dotenv()
    db_path = URL.create(
        drivername="postgresql",
        username=os.getenv("POSTGRES_USER"),
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT"),
        database=os.getenv("POSTGRES_DATABASE"),
        password=os.getenv("POSTGRES_PASSWORD")
    )
    return create_engine(db_path)


def connection():
    SessionClass = sessionmaker(bind=_init())
    return SessionClass()


if __name__ == '__main__':
    Base.metadata.create_all(_init())
