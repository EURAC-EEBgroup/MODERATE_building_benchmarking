from pydantic import BaseModel
from datetime import datetime
from typing import Union
import uuid

# class StoreBase(BaseModel):
#     store_name: str
#     surface: int
#     longitude: float
#     latitude: float
#     num_hvac: int 
#     cover_whole_building: bool


# class Store(StoreBase):
#     identifier: str


class Measurement(BaseModel):
    time: datetime
    sensor_id: str
    value: float