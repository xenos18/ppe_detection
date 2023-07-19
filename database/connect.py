from sqlalchemy import *
from sqlalchemy.orm import *
from database.models import *
from dotenv import load_dotenv
import os

load_dotenv()

url = f'postgresql+psycopg2://{os.environ["POSTGRES_USER"]}:{os.environ["POSTGRES_PASSWORD"]}@{os.environ["POSTGRES_HOST"]}:{os.environ["POSTGRES_PORT"]}/{os.environ["POSTGRES_DATABASE"]}'
engine = create_engine(url)
