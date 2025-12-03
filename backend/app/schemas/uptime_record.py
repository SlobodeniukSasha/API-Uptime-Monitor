from datetime import datetime
from pydantic.v1 import BaseModel


# -------- Base --------
class MonitorHistoryBase(BaseModel):
    status: str | None = None
    status_code: int | None = None
    response_time: float | None = None
    error_message: str | None = None


# -------- Create (internal) --------
class MonitorHistoryCreate(MonitorHistoryBase):
    monitor_id: int


# -------- Out --------
class MonitorHistoryOut(MonitorHistoryBase):
    id: int
    checked_at: datetime

    class Config:
        orm_mode = True