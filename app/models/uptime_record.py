from sqlalchemy import Column, Integer, ForeignKey, Float, DateTime, String

from app.core.database import Base


class MonitorHistory(Base):
    __tablename__ = "uptime_records"

    id = Column(Integer, primary_key=True)
    monitor_id = Column(Integer, ForeignKey("monitors.id"), nullable=False)
    status = Column(String)    # 'healthy', 'down', 'degraded'
    status_code = Column(Integer)    # 200, 300, 400, 500
    response_time = Column(Float)    # ms
    error_message = Column(String, default=None)
    checked_at = Column(DateTime, default=None)
