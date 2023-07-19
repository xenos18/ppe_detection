from sqlalchemy.orm import Session
from .models import LabEvent
from .create_tables import _init

if __name__ == '__main__':
    with Session(_init()) as session:
        lab_event = LabEvent(
            start_time='2022',
            end_time='2023',
            type='glove',
            frame='123.jpg',
            location=1
        )
        session.add(lab_event)
        session.commit()
