from datetime import datetime
from pydantic.v1 import BaseModel


class MonitorBase(BaseModel):
    name: str | None = None
    url: str
    expected_status_code: int = 200
    check_interval: int = 60
    is_active: bool = True


class MonitorCreate(MonitorBase):
    pass


class MonitorUpdate(BaseModel):
    name: str | None = None
    url: str | None = None
    expected_status_code: int | None = None
    check_interval: int | None = None
    is_active: bool | None = None


class MonitorOut(BaseModel):
    id: int
    url: str
    name: str
    created_at: datetime
    expected_status_code: int = 200
    check_interval: int
    created_at: datetime

    class Config:
        orm_mode = True
