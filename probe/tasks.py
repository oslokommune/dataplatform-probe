import asyncio
import logging
from threading import Thread
from datetime import datetime, timedelta, timezone

from tabulate import tabulate

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


async def clean_tasks(probe):
    interval = int(probe.config["CLEAN_TASKS_INTERVAL_SECONDS"])

    while True:
        await asyncio.sleep(interval)

        now = datetime.now(timezone.utc)
        dismiss_task_timeout = timedelta(
            seconds=probe.config["DISMISS_TASK_SECONDS"]
        )
        purgable_tasks = []

        # Dismiss old tasks
        for request_task in probe.request_tasks.values():
            if now > (request_task.time_created + dismiss_task_timeout):
                purgable_tasks.append(request_task)

        for task in purgable_tasks:
            probe.request_tasks.pop(request_task.seqno, None)

        logger.info(f"Cleaned tasks, removed={len(purgable_tasks)}")


async def print_tasks(probe, interval):
    headers = ["#", "State", "Created", "Succeeded", "Failed", "Duration"]

    while True:
        await asyncio.sleep(interval)

        rows = [
            [
                seqno,
                e.state.upper(),
                e.time_created,
                e.time_succeeded,
                e.time_failed,
                e.duration,
            ]
            for seqno, e in probe.request_tasks.items()
        ]

        print(tabulate(rows, headers=headers))
