from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship


class Base(DeclarativeBase):
    pass


class Location(Base):
    __tablename__ = "locations"
    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str] = mapped_column(String(50))
    place: Mapped[str] = mapped_column(String(150))
    lab = relationship("LabEvent")
    sh = relationship("ShEvent")

    def __repr__(self) -> str:
        return f"Location(id={self.id!r}, type={self.type!r}, place={self.place!r})"

    def serialize(self):
        return {
            'id': self.id,
            'type': self.type,
            'place': self.place,

        }


class LabEvent(Base):
    __tablename__ = "log_table_lab"
    id: Mapped[int] = mapped_column(primary_key=True)
    start_time: Mapped[str] = mapped_column(String(50))
    end_time: Mapped[str] = mapped_column(String(50))
    type: Mapped[str] = mapped_column(String(100))
    frame: Mapped[str] = mapped_column(String(100))
    location: Mapped[int] = mapped_column(ForeignKey("locations.id"))

    def __repr__(self) -> str:
        return f"LabEvent(id={self.id!r}, start_time={self.start_time!r}), end_time={self.end_time!r}), " \
               f"type={self.type!r}), frame={self.frame!r}), location={self.location!r})"


class ShEvent(Base):
    __tablename__ = "log_table_sh"
    id: Mapped[int] = mapped_column(primary_key=True)
    time_in: Mapped[str] = mapped_column(String(50))
    time_out: Mapped[str] = mapped_column(String(50))
    check_seq: Mapped[bool]
    sequence: Mapped[str] = mapped_column(String(100))
    frame: Mapped[str] = mapped_column(String(100))
    location: Mapped[int] = mapped_column(ForeignKey("locations.id"))

    def __repr__(self) -> str:
        return f"LabEvent(id={self.id!r}, time_in={self.time_in!r}), time_out={self.time_out!r}), " \
               f"check_seq={self.check_seq!r}), sequence={self.sequence!r}), frame={self.frame!r}), location={self.location!r})"
