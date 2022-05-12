import asyncio
import logging
import uuid
from datetime import datetime, timezone
from itertools import count

from prometheus_client import start_http_server

from .metrics import Metrics
from .models import RequestTask, RequestState
from .tasks import get_dataset

logger = logging.getLogger(__name__)


class Probe:
    def __init__(self, sdk, config):
        logger.info("Initializing probe application")

        self.app_id = str(uuid.uuid4())[:8]
        self.config = config
        self.sdk = sdk
        self.counter = count(start=1)
        self.metrics = Metrics()
        self.loop = asyncio.get_event_loop()

    def on_request_task_created(self, request_task: RequestTask):
        request_task.time_created = datetime.now(timezone.utc)
        request_task.state = RequestState.PENDING
        logger.debug(f"Request task created: {request_task}")
        self.metrics.requests_created.labels(self.app_id).inc()

    def on_request_task_success(self, request_task: RequestTask, data=None):
        request_task.time_succeeded = datetime.now(timezone.utc)
        request_task.state = RequestState.SUCCEEDED
        logger.info(
            f"Request task succeeded: {request_task} in {request_task.duration} seconds"
        )
        self.metrics.request_duration.set(request_task.duration)
        self.metrics.requests_succeeded.labels(self.app_id).inc()

    def on_request_task_fail(self, request: RequestTask, error=None):
        request.time_task_failed = datetime.now(timezone.utc)
        request.state = RequestState.FAILED
        logger.error(f"Request task failed: {request}, err={error}")
        self.metrics.requests_failed.labels(self.app_id).inc()

    def run(self):
        logger.info("Running probe")

        # Serve Prometheus metrics
        start_http_server(8000)

        self.loop.create_task(get_dataset(self))

        self.loop.run_forever()
