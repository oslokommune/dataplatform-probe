import asyncio
import logging
from threading import Thread
from datetime import datetime, timedelta

from .models import RequestTask

logger = logging.getLogger(__name__)


def _get_dataset_request(probe, request_task):
    dataset_id = probe.config["DATASET_ID"]

    try:
        logger.debug(f"{request_task}: Fetching dataset {dataset_id}")
        probe.sdk.get_dataset(
            datasetid=dataset_id,
            retries=3,
        )
    except Exception as e:
        probe.on_request_task_fail(request_task, e)
    else:
        probe.on_request_task_success(request_task)


async def get_dataset(probe):
    interval = timedelta(seconds=int(probe.config["TASK_INTERVAL_SECONDS"]))
    next_request = datetime.now() + timedelta(seconds=2)

    while True:
        sleep_time = (next_request - datetime.now()).total_seconds()
        logger.debug(f"Sleeping {sleep_time} seconds")
        await asyncio.sleep(sleep_time)

        request_task = RequestTask(app_id=probe.app_id, seqno=next(probe.counter))
        probe.on_request_task_created(request_task)

        Thread(target=_get_dataset_request, args=(probe, request_task)).start()

        next_request = next_request + interval
