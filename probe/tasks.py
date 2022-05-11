import asyncio
import logging
from threading import Thread
from datetime import datetime, timedelta, timezone

from tabulate import tabulate

from .models import Task

logger = logging.getLogger(__name__)


def _get_dataset_request(probe, task):
    dataset_id = probe.config["DATASET_ID"]

    try:
        logger.debug(f"{task}: Fetching dataset {dataset_id}")
        probe.sdk.get_dataset(
            datasetid=dataset_id,
            retries=3,
        )
    except Exception as e:
        probe.on_task_fail(task, e)
    else:
        probe.on_task_success(task)


async def get_dataset(probe):
    interval = timedelta(seconds=int(probe.config["TASK_INTERVAL_SECONDS"]))
    next_task = datetime.now() + timedelta(seconds=2)

    while True:
        sleep_time = (next_task - datetime.now()).total_seconds()
        logger.debug(f"Sleeping {sleep_time} seconds")
        await asyncio.sleep(sleep_time)

        task = Task(app_id=probe.app_id, seqno=next(probe.counter))
        probe.on_task_created(task)

        Thread(target=_get_dataset_request, args=(probe, task)).start()

        next_task = next_task + interval


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
        for task in probe.tasks.values():
            if now > (task.time_created + dismiss_task_timeout):
                purgable_tasks.append(task)

        for task in purgable_tasks:
            probe.tasks.pop(task.seqno, None)

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
            for seqno, e in probe.tasks.items()
        ]

        print(tabulate(rows, headers=headers))
