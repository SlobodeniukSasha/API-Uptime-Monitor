from datetime import datetime

from sqlalchemy import Column, Integer, ForeignKey, Float, DateTime, String, Text, func
from sqlalchemy.orm import relationship

from ..core.database import Base


class MonitorHistory(Base):
    __tablename__ = "monitor_history"

    id = Column(Integer, primary_key=True)
    monitor_id = Column(Integer, ForeignKey("monitors.id"), nullable=False)

    status = Column(String)  # 'healthy', 'down', 'degraded'
    status_code = Column(Integer)  # 200, 300, 400, 500
    latency = Column(Float)  # ms
    error_message = Column(Text, default=None)
    checked_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    monitor = relationship("Monitor", back_populates="history")
    problem = relationship("Problem", back_populates="history")
