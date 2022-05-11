import asyncio
import json
import logging
import uuid
from datetime import datetime, timedelta, timezone
from itertools import count

from prometheus_client import start_http_server

from .metrics import Metrics
from .models import Task, TaskState
from .tasks import (
    clean_task_backlog,
    get_dataset,
)

logger = logging.getLogger(__name__)


class Probe:
    def __init__(self, sdk, config):
        logger.info("Initializing probe application")

        self.app_id = str(uuid.uuid4())[:8]
        self.config = config
        self.sdk = sdk
        self.counter = count(start=1)
        self.backlog = {}
        self.metrics = Metrics()
        self.loop = asyncio.get_event_loop()

    def on_task_created(self, task: Task):
        task.time_created = datetime.now(timezone.utc)
        task.state = TaskState.PENDING
        self.backlog[task.seqno] = task
        logger.debug(f"Task created: {task}")
        self.metrics.tasks_created.labels(self.app_id).inc()

    def on_task_success(self, task: Task, data=None):
        task.time_succeeded = datetime.now(timezone.utc)
        task.state = TaskState.SUCCEEDED
        logger.info(f"Task completed: {task} in {task.duration} seconds")
        self.metrics.task_duration.set(task.duration)
        self.metrics.tasks_succeeded.labels(self.app_id).inc()

    def on_task_fail(self, task: Task, error=None):
        task.time_failed = datetime.now(timezone.utc)
        task.state = TaskState.FAILED
        logger.error(f"Task failed: {task}, err={error}")
        self.metrics.tasks_failed.labels(self.app_id).inc()

    def run(self):
        logger.info("Running probe")

        # Serve Prometheus metrics
        start_http_server(8000)

        self.loop.create_task(get_dataset(self))
        self.loop.create_task(clean_task_backlog(self))

        self.loop.run_forever()
