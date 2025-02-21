from sqlalchemy import Column, Double, ForeignKey, DateTime, event, DDL, UUID, UniqueConstraint
from app.database import Base


# class Store(Base):
#     __tablename__ = "store"

#     identifier = Column(String, primary_key=True, nullable=False)
#     store_name = Column(String, nullable=False)
#     surface = Column(Integer, nullable=False)
#     longitude = Column(Double, nullable=False)
#     latitude = Column(Double, nullable=False)
#     num_hvac = Column(Integer, nullable=False)
#     cover_whole_building = Column(Boolean, nullable=False)


class Measurement(Base):
    __tablename__ = "measurement"

    time = Column(DateTime, primary_key=True, nullable=False)
    sensor_id = Column(UUID, primary_key=True, nullable=False)
    value = Column(Double, nullable=False)
    __table_args__ = (UniqueConstraint('time', 'sensor_id', name='_time_sensor_id'),)

event.listen(
    Measurement.__table__,
    'after_create',
    DDL(f"SELECT create_hypertable('{Measurement.__tablename__}', 'time', if_not_exists => TRUE, create_default_indexes => TRUE);")
)


