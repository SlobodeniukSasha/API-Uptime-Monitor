import asyncio
import httpx
from datetime import datetime, timezone

from backend.app.services.duckduckgo import duckduckgo_search
from backend.app.services.ai_analysis import ai_analyze_issue
from backend.app.core.celery_app import celery
from backend.app.core.database import sync_session_maker

from backend.app.models import Monitor, MonitorHistory, Problem
from backend.app.tasks.alerts import send_alert_email


@celery.task
def check_monitor(monitor_id: int):
    return asyncio.run(_check_monitor_async(monitor_id))


async def _check_monitor_async(monitor_id: int):
    with sync_session_maker() as session:
        monitor = session.get(Monitor, monitor_id)

        if not monitor or not monitor.is_active:
            return

        try:
            with httpx.Client(timeout=10) as client:
                response = client.get(monitor.url)
                status_code = response.status_code
                latency = response.elapsed.total_seconds() * 1000
                error_message = None
        except Exception as e:
            status_code = None
            latency = None
            error_message = str(e)

        if error_message is not None:
            status = "down"
        elif status_code != monitor.expected_status_code:
            status = "degraded"
            error_message = f"Unexpected status code: {status_code}"
        else:
            status = "healthy"

        history = MonitorHistory(
            monitor_id=monitor_id,
            status=status,
            status_code=status_code,
            latency=latency,
            error_message=error_message,
            checked_at=datetime.now(timezone.utc)
        )

        session.add(history)
        session.flush()

        if error_message:
            try:
                ddg = await duckduckgo_search(f"Why {monitor.url} is down, {error_message}")

                print(ddg)

                if ddg:
                    ai_analysis, ai_recommendations = await ai_analyze_issue(
                        url=monitor.url,
                        error_message=error_message,
                        ddg_results=ddg,
                    )
                else:
                    ai_analysis, ai_recommendations = "Search for solutions failed", "Check the error manually"

            except Exception as e:
                print(f"Error in problem analysis: {e}")
                ai_analysis, ai_recommendations = "Analysis error", str(e)

            print("-" * 50)
            print('AI Analysis: ', ai_analysis)
            print('AI Recommendations: ', ai_recommendations)
            print("-" * 50)

            send_alert_email.delay(
                user_email=monitor.owner.email,
                monitor_name=monitor.name,
                monitor_user_name=monitor.owner.full_name,
                monitor_url=monitor.url,
                monitor_status=status_code,
                ai_recommendations=ai_recommendations,
                monitor_check_interval=monitor.check_interval,
            )

            problem = Problem(
                history_id=history.id,
                monitor_id=monitor_id,
                duckduckgo_search_data=ddg,
                ai_analysis=ai_analysis,
                ai_recommendations=ai_recommendations
            )
            session.add(problem)

        session.commit()

        return {"monitor_id": monitor_id, "status": status}
