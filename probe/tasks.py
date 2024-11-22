import asyncio
import logging
from threading import Thread
from datetime import datetime, timedelta

import requests

from .models import RequestTask

logger = logging.getLogger(__name__)


def _get_dataset_request(probe, request_task):
    dataset_id = probe.config["DATASET_ID"]

    try:
        logger.debug(f"{request_task}: Fetching dataset {dataset_id}")
        probe.sdk.get_dataset(dataset_id, retries=3)
    except Exception as e:
        probe.on_request_task_fail(request_task, e)
    else:
        probe.on_request_task_success(request_task)

        if url := probe.config["BETTERUPTIME_HEARTBEAT_URL"]:
            _send_successful_dataset_request_heartbeat(url)


def _send_successful_dataset_request_heartbeat(url):
    try:
        logger.info("Heartbeat sent")
        response = requests.head(url)
        response.raise_for_status()
    except requests.RequestException as e:
        status_code = getattr(e.response, "status_code", None)
        logger.error(
            "Heartbeat request failed{}".format(
                f" ({status_code})" if status_code else ""
            )
        )


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
