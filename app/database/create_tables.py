from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base
from .main_db import add_location
from sqlalchemy.engine import URL
from dotenv import load_dotenv
import os

load_dotenv()

url = f'postgresql+psycopg2://{os.environ["POSTGRES_USER"]}:{os.environ["POSTGRES_PASSWORD"]}@{os.environ["POSTGRES_HOST"]}:' \
      f'{os.environ["POSTGRES_PORT"]}/{os.environ["POSTGRES_DATABASE"]}'
engine = create_engine(url)


def _init():
    db_path = URL.create(
        drivername="postgresql",
        username=os.getenv("POSTGRES_USER"),
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT"),
        database=os.getenv("POSTGRES_DATABASE"),
        password=os.getenv("POSTGRES_PASSWORD")
    )
    add_location('gateway', 'one')
    return create_engine(db_path)


if __name__ == '__main__':
    Base.metadata.create_all(_init())

