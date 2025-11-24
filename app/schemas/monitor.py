from datetime import datetime
from pydantic.v1 import BaseModel


class MonitorCreate(BaseModel):
    url: str
    name: str
    expected_status_code: int = 200
    check_interval: int = 60


class MonitorOut(BaseModel):
    id: int
    url: str
    name: str
    expected_status_code: int = 200
    check_interval: int
    created_at: datetime

    class Config:
        orm_mode = True
