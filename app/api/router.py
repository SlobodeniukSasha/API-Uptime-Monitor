from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.monitors_crud import MonitorCRUD
from app.core.database import get_async_session
from app.schemas.monitor import MonitorOut, MonitorCreate

router = APIRouter(
    prefix="/monitors",
    tags=["Monitor Operation"]
)


@router.post("/", response_model=MonitorOut, status_code=201)
async def create_monitor(data: MonitorCreate, db: AsyncSession = Depends(get_async_session)):
    return await MonitorCRUD.create(db, data)


@router.delete("/{monitor_id}/", status_code=200)
async def delete_monitor(monitor_id, db: AsyncSession = Depends(get_async_session)):
    return await MonitorCRUD.delete(db, monitor_id)


@router.get("/", response_model=list[MonitorOut])
async def get_all_monitors(
        skip: int = 0,
        limit: int = 100,
        db: AsyncSession = Depends(get_async_session)
):
    return await MonitorCRUD.get_all(db, skip, limit)


@router.get("/{monitor_id}/", response_model=MonitorOut)
async def get_monitor(monitor_id: int, db: AsyncSession = Depends(get_async_session)):
    monitor = await MonitorCRUD.get_by_id(db, monitor_id)
    if not monitor:
        raise HTTPException(status_code=404, detail="Monitor not found")
    return monitor


@router.get("/{monitor_id}/history/")
async def get_monitors_history(
        monitor_id: int,
        limit: int = 100,
        db: AsyncSession = Depends(get_async_session)
):
    records = await MonitorCRUD.get_history(db, monitor_id)
    if not records:
        raise HTTPException(status_code=404, detail="Records not found")

    return await MonitorCRUD.get_history(db, monitor_id, limit)
