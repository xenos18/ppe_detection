import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

con = psycopg2.connect(
  database=os.environ["POSTGRES_DATABASE"],
  user=os.environ["POSTGRES_USER"],
  password=os.environ["POSTGRES_PASSWORD"],
  host=os.environ["POSTGRES_HOST"],
  port=os.environ["POSTGRES_PORT"]
)
con.autocommit = True
cur = con.cursor()


def add_location(type, place):
    cur.execute(
        f"""INSERT INTO locations(type, place)
           VALUES('{type}', '{place}');"""
    )


def add_sh_event(location_id, time_in, time_out, check, sequence, frame):
    cur.execute(
        f"""INSERT INTO log_table_sh(id, time_in, time_out, check_seq, sequence, frame)
        VALUES('{location_id}', '{time_in}', '{time_out}', '{check}', '{sequence}', '{frame}');"""
    )


def add_lab_event(location_id, start_time, end_time, type, frame):
    cur.execute(
        f"""INSERT INTO log_table_lab(id, start_time, end_time, type, frame)
        VALUES('{location_id}', '{start_time}', '{end_time}', '{type}', '{frame}');"""
    )