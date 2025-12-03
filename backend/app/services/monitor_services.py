from typing import Optional, Sequence

from sqlalchemy.orm import selectinload

from ..models.monitor import Monitor
from ..models.problem import Problem
from ..models.monitor_history import MonitorHistory
from ..schemas.monitor import MonitorCreate
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class MonitorCRUD:
    @staticmethod
    async def create(
            db: AsyncSession,
            data: MonitorCreate,
            owner_id: int
    ) -> Monitor:
        monitor_data = data.dict()
        monitor_data["owner_id"] = owner_id

        monitor = Monitor(**monitor_data)
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
    async def get_all(db: AsyncSession, current_user: int, skip: int = 0, limit: int = 100) -> Sequence[Monitor]:
        stmt = (
            select(Monitor)
            .where(Monitor.owner_id == current_user)
            .order_by(Monitor.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def get_by_id(db: AsyncSession, current_user: int, monitor_id: int) -> Optional[Monitor]:
        result = await db.execute(
            select(Monitor)
            .where(
                Monitor.id == monitor_id,
                Monitor.owner_id == current_user
            )
        )
        return result.scalar_one_or_none()


class HistoryCRUD:
    @staticmethod
    async def get_history(db: AsyncSession, current_user: int, monitor_id: int, limit: int = 10) -> Sequence[MonitorHistory]:
        result = await db.execute(
            select(MonitorHistory)
            .where(
                MonitorHistory.monitor_id == monitor_id,

                # Monitor.owner_id == current_user
            )
            .order_by(MonitorHistory.checked_at.desc())
            .limit(limit)
        )
        return result.scalars().all()

    @staticmethod
    async def get_problem_history(db: AsyncSession, current_user: int, monitor_id: int, limit: int = 10) -> Sequence[MonitorHistory]:
        result = await db.execute(
            select(MonitorHistory)
            .where(
                MonitorHistory.monitor_id == monitor_id,
                Monitor.owner_id == current_user,
                MonitorHistory.error_message.isnot(None)
            )
            .order_by(MonitorHistory.checked_at.desc())
            .limit(limit)
        )
        return result.scalars().all()

    @staticmethod
    async def get_problem_with_analysis(db: AsyncSession, current_user: int, problem_id: int, monitor_id: int) -> Problem:
        result = await db.execute(
            select(Problem)
            .options(selectinload(Problem.history))
            .where(
                Problem.id == problem_id,
                Monitor.owner_id == current_user,
                Problem.monitor_id == monitor_id
            )
        )
        return result.scalar_one_or_none()
