from datetime import datetime
from typing import Literal

from pydantic import BaseModel

Status = Literal["NORMAL", "WARNING", "DANGER"]


class Reading(BaseModel):
    id: int
    ts: datetime  # stored as unix epoch; pydantic converts it to a UTC datetime
    gas: float
    temp: float
    humidity: float
    status: Status


class Thresholds(BaseModel):
    gas: float
    temp_high: float
    humidity_low: float
