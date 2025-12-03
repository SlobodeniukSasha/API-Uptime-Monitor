from ..core.database import Base
from sqlalchemy import Column, Integer, String, DateTime, func, Boolean, ForeignKey
from sqlalchemy.orm import relationship


class Monitor(Base):
    __tablename__ = 'monitors'

    id = Column(Integer, primary_key=True)
    url = Column(String, nullable=False)
    name = Column(String, default=url)

    expected_status_code = Column(Integer, default=200)  # 200, 300, 400, 500

    check_interval = Column(Integer, default=60)
    is_active = Column(Boolean, default=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="monitors")

    history = relationship("MonitorHistory", back_populates="monitor")
    problem = relationship("Problem", back_populates="monitor")
