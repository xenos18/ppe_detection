from sqlalchemy import create_engine, ForeignKey, select
from sqlalchemy.orm import Session
from models import Base, Location, ShEvent, LabEvent
from dotenv import load_dotenv
import os

load_dotenv()

url = f'postgresql+psycopg2://{os.environ["POSTGRES_USER"]}:{os.environ["POSTGRES_PASSWORD"]}@{os.environ["POSTGRES_HOST"]}:' \
      f'{os.environ["POSTGRES_PORT"]}/{os.environ["POSTGRES_DATABASE"]}'
engine = create_engine(url)

if __name__ == '__main__':
      with Session(engine) as session:
            lab_event = LabEvent(
                  start_time='2022',
                  end_time='2023',
                  type='glove',
                  frame='123.jpg',
                  location=1
            )
            session.add(lab_event)
            session.commit()