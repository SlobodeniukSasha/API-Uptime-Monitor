from datetime import datetime, UTC
import time

import httpx
from app.core.celery_app import celery
from app.core.database import get_async_session
from app.models.monitor import Monitor
from app.models.uptime_record import UptimeRecord


@celery.task
async def check_monitor_health(monitor_id: int):
    async with get_async_session() as db:
        monitor = await db.get(Monitor, monitor_id)

        if not monitor:
            return

        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(monitor.url)

            ok = response.status_code == monitor.expected_status
            latency = response.elapsed.total_seconds() * 1000

            if response.status_code == monitor.expected_status:
                status = "healthy"
            elif 200 <= response.status_code < 500:
                status = "degraded"
            else:
                status = "down"

            record = UptimeRecord(
                monitor_id=monitor_id,
                status=status,  # 'healthy', 'down', 'degraded'
                status_code=ok,  # 200, 300, 400, 500
                response_time=latency,  # ms
                checked_at=datetime.now(UTC)
            )
            db.add(record)
            await db.commit()

            if status == "down":
                await send_alert(monitor, status)

        except Exception as e:
            record = UptimeRecord(
                monitor_id=monitor_id,
                status='down',  # 'healthy', 'down'
                status_code=None,  # 200, 300, 400, 500
                response_time=None,
                error_message=str(e),
                checked_at=datetime.now(UTC)
            )

            db.add(record)
            await db.commit()

            send_alert(monitor, "down")
