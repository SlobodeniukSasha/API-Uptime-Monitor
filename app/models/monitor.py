from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, func

from app.core.database import Base


class Monitor(Base):
    __tablename__ = 'monitors'

    id = Column(Integer, primary_key=True)
    url = Column(String, nullable=False)
    name = Column(String)
    expected_status_code = Column(Integer, default=200)    # 200, 300, 400, 500
    check_interval = Column(Integer, default=60)
    created_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        server_default=func.now(),
        nullable=False
    )

