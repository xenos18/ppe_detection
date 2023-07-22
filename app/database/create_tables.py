from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base
from sqlalchemy.engine import URL
from dotenv import load_dotenv
import os

load_dotenv()

url = f'postgresql+psycopg2://{os.environ["POSTGRES_USER"]}:{os.environ["POSTGRES_PASSWORD"]}@{os.environ["POSTGRES_HOST"]}:' \
      f'{os.environ["POSTGRES_PORT"]}/{os.environ["POSTGRES_DATABASE"]}'
engine = create_engine(url)


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

def run():
    Base.metadata.create_all(_init())


if __name__ == '__main__':
    run()
