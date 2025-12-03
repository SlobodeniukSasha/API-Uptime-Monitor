from sqlalchemy import Column, Integer, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship

from ..core.database import Base


class Problem(Base):
    __tablename__ = "problem"

    id = Column(Integer, primary_key=True)
    history_id = Column(Integer, ForeignKey("monitor_history.id"), nullable=False)
    monitor_id = Column(Integer, ForeignKey("monitors.id"), nullable=False)

    duckduckgo_search_data = Column(JSON, nullable=True)
    ai_analysis = Column(Text, nullable=True)
    ai_recommendations = Column(Text, nullable=True)

    history = relationship("MonitorHistory", back_populates="problem")
    monitor = relationship("Monitor", back_populates="problem")
