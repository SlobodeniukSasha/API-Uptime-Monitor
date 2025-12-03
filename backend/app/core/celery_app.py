from celery import Celery

from backend.app.core.config import settings

celery = Celery(
    "health_monitor",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery.autodiscover_tasks(['backend.app.tasks'])

celery.conf.beat_schedule = {
    'schedule-dynamic-monitoring': {
        'task': 'backend.app.tasks.scheduler.schedule_monitoring',
        'schedule': 1.0,
    },
}

import backend.app.tasks.scheduler
