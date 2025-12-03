from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.auth.dependencies import get_current_user
from backend.app.core.database import get_async_session
from backend.app.models import User
from backend.app.schemas.monitor import MonitorOut, MonitorCreate
from backend.app.services.monitor_services import MonitorCRUD, HistoryCRUD

router = APIRouter(
    prefix="/monitors",
    tags=["Monitor Operation"]
)


@router.post("/", response_model=MonitorOut, status_code=201)
async def create_monitor(
        data: MonitorCreate,
        db: AsyncSession = Depends(get_async_session),
        current_user: User = Depends(get_current_user)
):
    return await MonitorCRUD.create(db, data, current_user.id)


@router.delete("/{monitor_id}/", status_code=200)
async def delete_monitor(
        monitor_id,
        db: AsyncSession = Depends(get_async_session),
        current_user: User = Depends(get_current_user)
):
    return await MonitorCRUD.delete(db, monitor_id)


@router.get("/", response_model=list[MonitorOut])
async def get_all_monitors(
        skip: int = 0,
        limit: int = 100,
        db: AsyncSession = Depends(get_async_session),
        current_user: User = Depends(get_current_user)

):
    return await MonitorCRUD.get_all(db=db, current_user=current_user.id, skip=skip, limit=limit)


@router.get("/{monitor_id}/", response_model=MonitorOut)
async def get_monitor(
        monitor_id: int,
        db: AsyncSession = Depends(get_async_session),
        current_user: User = Depends(get_current_user)
):
    monitor = await MonitorCRUD.get_by_id(db=db, current_user=current_user.id, monitor_id=monitor_id)
    if not monitor:
        raise HTTPException(status_code=404, detail="Monitor not found")
    return monitor


@router.get("/{monitor_id}/history/")
async def get_monitor_history(
        monitor_id: int,
        limit: int = 10,
        db: AsyncSession = Depends(get_async_session),
        current_user: User = Depends(get_current_user)
):
    history = await HistoryCRUD.get_history(
        db=db,
        current_user=current_user.id,
        monitor_id=monitor_id,
        limit=limit
    )
    if not history:
        raise HTTPException(status_code=404, detail="History for this monitor not found")

    return {
        "monitor_id": monitor_id,
        "total_records": len(history),
        "history": [
            {
                "id": record.id,
                "status": record.status,
                "status_code": record.status_code,
                "latency": record.latency,
                "error_message": record.error_message,
                "checked_at": record.checked_at.isoformat()
            }
            for record in history
        ]
    }


@router.get("/{monitor_id}/problem_history/")
async def get_monitor_problems(
        monitor_id: int,
        limit: int = 10,
        db: AsyncSession = Depends(get_async_session),
        current_user: User = Depends(get_current_user)
):
    """
    Get only problem history (with error_messages)
    """
    problem_history = await HistoryCRUD.get_problem_history(
        db=db,
        current_user=current_user.id,
        monitor_id=monitor_id,
        limit=limit
    )

    if not problem_history:
        raise HTTPException(status_code=404, detail="Problem History for this monitor not found")

    return {
        "monitor_id": monitor_id,
        "problems_count": len(problem_history),
        "problems": [
            {
                "id": record.id,
                "status": record.status,
                "status_code": record.status_code,
                "latency": record.latency,
                "error_message": record.error_message,
                "checked_at": record.checked_at.isoformat(),
            }
            for record in problem_history
        ]
    }


@router.get("/{monitor_id}/problem_history/{problem_id}/")
async def get_more_about_current_monitor_problem(
        monitor_id: int,
        problem_id: int,
        db: AsyncSession = Depends(get_async_session),
        current_user: User = Depends(get_current_user)
):
    """
    Get details about problem (AI summary and the reasons by DuckDuckGo)
    """

    problem = await HistoryCRUD.get_problem_with_analysis(
        db=db,
        current_user=current_user.id,
        problem_id=problem_id,
        monitor_id=monitor_id,
    )
    if not problem:
        raise HTTPException(status_code=404, detail="Problem record not found")

    return {
        "monitor_id": monitor_id,
        "problem":
            {
                "id": problem.id,
                "monitor_id": problem.monitor_id,
                "error_message": problem.history.error_message,
                "duckduckgo_search_data": problem.duckduckgo_search_data,
                "ai_analysis": problem.ai_analysis,
                "ai_recommendations": problem.ai_recommendations,
            }
    }
