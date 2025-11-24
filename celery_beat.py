from app.core.celery_app import celery
from celery.schedules import crontab

celery.conf.beat_schedule = {
    "check-every-minute": {
        "task": "app.tasks.checks.check_monitor",
        "schedule": crontab(minute="*/1"),
        "args": (1,)  # временно жёстко один монитор для примера
    }
}
