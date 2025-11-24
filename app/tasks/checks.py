import logging
from datetime import datetime, UTC

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.celery_app import celery
from app.core.database import get_async_session
from app.models.monitor import Monitor
from app.models.uptime_record import MonitorHistory

logger = logging.getLogger(__name__)


@celery.task
async def check_monitor_health(monitor_id: int):
    async with get_async_session() as db:
        try:
            monitor = await db.get(Monitor, monitor_id)
            if not monitor:
                logger.warning(f"Monitor {monitor_id} not found")
                return

            if not monitor.url or not monitor.url.startswith(('http://', 'https://')):
                raise ValueError(f"Invalid URL: {monitor.url}")

            monitor_data = await _perform_health_check(monitor)

            new_monitor_history = MonitorHistory(
                monitor_id=monitor_id,
                **monitor_data
            )

            db.add(new_monitor_history)
            await db.commit()

            if monitor_data['status'] in ['down', 'degraded']:
                await _send_alert_safely(monitor, monitor_data)

            logger.info(f"Health check completed for {monitor.url}: {monitor_data['status']}")

        except Exception as e:
            await _handle_check_error(db, monitor_id, e, monitor)


async def _perform_health_check(monitor: Monitor) -> dict:
    """Performs HTTP validation and returns data for writing"""
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.get(monitor.url)

        latency = response.elapsed.total_seconds() * 1000
        status = _determine_status(response.status_code, monitor.expected_status_code, latency)

        return {
            'status': status,
            'status_code': response.status_code,
            'response_time': latency,
            'error_message': None,
            'checked_at': datetime.now(UTC)
        }

    except httpx.TimeoutException:
        return {
            'status': 'down',
            'status_code': None,
            'response_time': None,
            'error_message': 'Request timeout (5s)',
            'checked_at': datetime.now(UTC)
        }

    except httpx.ConnectError:
        return {
            'status': 'down',
            'status_code': None,
            'response_time': None,
            'error_message': 'Connection failed - host unreachable',
            'checked_at': datetime.now(UTC)
        }

    except httpx.HTTPError as e:
        return {
            'status': 'down',
            'status_code': None,
            'response_time': None,
            'error_message': f'HTTP error: {str(e)}',
            'checked_at': datetime.now(UTC)
        }


def _determine_status(status_code: int, expected_status: int, latency: float) -> str:
    """Determines the status based on the response code and latency"""
    if status_code == expected_status:
        if latency < 1000:
            return "healthy"
        else:
            return "degraded"

    elif 200 <= status_code < 400:
        return "degraded"

    elif status_code >= 400:
        return "down"

    else:
        return "down"


async def _handle_check_error(db: AsyncSession, monitor_id: int, error: Exception, monitor=None):
    """Handles errors during validation"""
    error_message = f"{type(error).__name__}: {str(error)}"

    record = MonitorHistory(
        monitor_id=monitor_id,
        status='down',
        status_code=None,
        response_time=None,
        error_message=error_message,
        checked_at=datetime.now(UTC)
    )

    try:
        db.add(record)
        await db.commit()

        if monitor:
            await _send_alert_safely(monitor, {
                'status': 'down',
                'error_message': error_message
            })

    except Exception as db_error:
        logger.error(f"Failed to save error record: {db_error}")

    logger.error(f"Health check failed for monitor {monitor_id}: {error_message}")


async def _send_alert_safely(monitor: Monitor, check_data: dict):
    """Safely sends an alert with error handling"""
    try:
        await send_alert(
            monitor=monitor,
            status=check_data['status'],
            status_code=check_data.get('status_code'),
            error_message=check_data.get('error_message'),
            response_time=check_data.get('response_time')
        )
    except Exception as alert_error:
        logger.error(f"Failed to send alert for monitor {monitor.id}: {alert_error}")
