import asyncio
from logging import getLogger, basicConfig, DEBUG, FileHandler, ERROR, StreamHandler, Formatter

import httpx
from datetime import datetime, timezone

from backend.app.services.duckduckgo import duckduckgo_search
from backend.app.services.ai_analysis import ai_analyze_issue
from backend.app.core.celery_app import celery
from backend.app.core.database import sync_session_maker

from backend.app.models import Monitor, MonitorHistory, Problem
from backend.app.tasks.alerts import send_alert_email


logger = getLogger('monitoring')

FORMAT = '%(asctime)s : %(name)s : %(levelname)s : %(message)s'
formatter = Formatter(FORMAT)


file_handler = FileHandler("data.log")
file_handler.setLevel(DEBUG)
file_handler.setFormatter(formatter)

console = StreamHandler()
console.setLevel(ERROR)
console.setFormatter(formatter)

basicConfig(level=DEBUG, format=FORMAT, handlers=[file_handler, console])


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
            logger.info(f'Monitor {monitor.name} receive unexpected response')
            try:
                ddg = await duckduckgo_search(f"Why {monitor.url} is down, {error_message}")

                logger.info('-' * 50)
                logger.info(f'DDg:  {ddg}')
                logger.info('-' * 50)

                if ddg:
                    ai_analysis, ai_recommendations = await ai_analyze_issue(
                        url=monitor.url,
                        error_message=error_message,
                        ddg_results=ddg,
                    )
                else:
                    logger.error('Something went wrong with duckduckgo_search ')
                    ai_analysis, ai_recommendations = "Search for solutions failed", "Check the error manually"

            except Exception as e:
                logger.error(f"Error in problem analysis: {e}")
                ai_analysis, ai_recommendations = "Analysis error", str(e)

            logger.info('-' * 50)
            logger.info('AI Analysis: ' + ai_analysis)
            logger.info('AI Recommendations: ' + ai_recommendations)
            logger.info('-' * 50)

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
