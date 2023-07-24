from sqlalchemy import create_engine, ForeignKey, select
from sqlalchemy.orm import Session
from database.models import Base, Location, ShEvent, LabEvent
from dotenv import load_dotenv
import os

load_dotenv()

url = f'postgresql+psycopg2://{os.environ["POSTGRES_USER"]}:{os.environ["POSTGRES_PASSWORD"]}@{os.environ["POSTGRES_HOST"]}:' \
      f'{os.environ["POSTGRES_PORT"]}/{os.environ["POSTGRES_DATABASE"]}'
engine = create_engine(url)


def add_sh_event(time_in, time_out, check_seq, frame):
      with Session(engine) as session:
            sh_event = ShEvent(
                  time_in=time_in,
                  time_out=time_out,
                  check_seq=check_seq,
                  frame=frame,
                  location=1
            )
            session.add(sh_event)
            session.commit()


def add_location(type, place):
      with Session(engine) as session:
            loc = Location(
                  type=type,
                  place=place
            )
            session.add(loc)
            session.commit()


def add_lab_event(start_time, end_time, type, frame):
      with Session(engine) as session:
            event = LabEvent(
                  start_time=start_time,
                  end_time=end_time,
                  type=type,
                  frame=frame,
                  location=1
            )
            session.add(event)
            session.commit()
