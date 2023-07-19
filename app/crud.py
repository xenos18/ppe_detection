from sqlalchemy.orm import Session
from database import models


def get_location(db: Session):
    return db.query(models.Location).all()


def get_events_sh(db: Session):
    return db.query(models.ShEvent).all()


def get_events_lab(db: Session):
    return db.query(models.LabEvent).all()
