from datetime import datetime, timezone, timedelta

from backend.app.core.celery_app import celery
from backend.app.core.database import sync_session_maker
from backend.app.models import Monitor
from .monitoring_tasks import check_monitor


@celery.task
def schedule_monitoring():
    with sync_session_maker() as session:
        monitors = session.query(Monitor).filter(Monitor.is_active == True).all()

        now = datetime.now(timezone.utc)

        for monitor in monitors:
            last_history = monitor.history[-1] if monitor.history else None

            if not last_history:
                check_monitor.delay(monitor.id)
                continue

            last_check = last_history.checked_at
            last_check = last_check.astimezone(timezone.utc)
            interval = monitor.check_interval

            time_passed = (now - last_check).total_seconds()
            # print('-----------')
            # print('Monitor name: ', monitor.name)
            # print('Now: ', now)
            # print('Last Check: ', last_check)
            # print('Time passed: ', time_passed)
            # print('Interval: ', interval)
            # print('-----------')

            if time_passed > interval * 10:
                print(f"Updating the time of last check (was: {last_check})")
                last_history.checked_at = now - timedelta(seconds=interval - 1)
                session.commit()
                session.refresh(last_history)
                print(f"Now: {last_history.checked_at}")
                check_monitor.delay(monitor.id)
            elif time_passed >= interval:
                print(f'Monitor {monitor.name} send to check')
                check_monitor.delay(monitor.id)

            # if time_passed >= interval:
            #     check_monitor.delay(monitor.id)
