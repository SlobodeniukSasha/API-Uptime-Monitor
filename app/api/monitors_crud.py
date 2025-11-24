from typing import List, Optional, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import UptimeRecord
from app.models.monitor import Monitor
from app.schemas.monitor import MonitorCreate


class MonitorCRUD:
    @staticmethod
    async def create(db: AsyncSession, data: MonitorCreate) -> Monitor:
        monitor = Monitor(**data.dict())
        db.add(monitor)
        await db.commit()
        await db.refresh(monitor)
        return monitor

    @staticmethod
    async def delete(db: AsyncSession, monitor_id):
        monitor = await db.get(Monitor, monitor_id)
        if not monitor:
            return {'status_code': '404', 'detail': 'Monitor not found'}

        await db.delete(monitor)
        await db.commit()
        return {'status_code': '200', 'detail': 'Deleted'}

    @staticmethod
    async def get_all(db: AsyncSession, skip: int = 0, limit: int = 100) -> Sequence[Monitor]:
        result = await db.execute(
            select(Monitor)
            .offset(skip)
            .limit(limit)
            .order_by(Monitor.created_at.desc())
        )
        return result.scalars().all()

    @staticmethod
    async def get_by_id(db: AsyncSession, monitor_id: int) -> Optional[Monitor]:
        result = await db.execute(
            select(Monitor).where(Monitor.id == monitor_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_history(db: AsyncSession, monitor_id: int, limit: int = 100) -> Sequence[UptimeRecord]:
        result = await db.execute(
            select(UptimeRecord)
            .where(UptimeRecord.monitor_id == monitor_id)
            .order_by(UptimeRecord.checked_at.desc())
            .limit(limit)
        )
        return result.scalars().all()
