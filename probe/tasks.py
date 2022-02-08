import asyncio
import logging
from threading import Thread
from datetime import datetime, timedelta, timezone

from tabulate import tabulate

from .models import Event, EventState

logger = logging.getLogger(__name__)


def _post_request(probe, event):
    try:
        logger.debug(f"Posting event {event}")
        probe.sdk.post_event(
            {
                "app_id": event.app_id,
                "seqno": event.seqno,
                "time_sent": event.time_sent.isoformat(),
            },
            probe.config["DATASET_ID"],
            probe.config["DATASET_VERSION"],
            retries=3,
        )

    except Exception as e:
        logger.error(f"Event emit failed: event={event}, err={e}")
        probe.on_event_post_error(event)
    else:
        logger.debug(f"Event posted: {event}")
        probe.on_event_posted(event)


async def post_event(probe):
    interval = timedelta(seconds=int(probe.config["EVENT_INTERVAL_SECONDS"]))
    next_send = datetime.now() + timedelta(seconds=2)

    while True:
        sleep_time = (next_send - datetime.now()).total_seconds()
        logger.debug(f"Sleeping {sleep_time} seconds")
        await asyncio.sleep(sleep_time)

        # Create new event
        event = Event(app_id=probe.app_id, seqno=next(probe.counter))

        probe.on_event_post(event)
        Thread(target=_post_request, args=(probe, event)).start()

        next_send = next_send + interval

        # Count connected listeners
        probe.metrics.event_listeners_connected_count.labels(probe.app_id).set(
            len([li for li in probe.listeners if li.connected])
        )


async def clean_events(probe):
    interval = int(probe.config["CLEAN_EVENTS_INTERVAL_SECONDS"])

    while True:
        await asyncio.sleep(interval)

        now = datetime.now(timezone.utc)
        dismiss_event_timeout = timedelta(
            seconds=probe.config["DISMISS_EVENT_TIMEOUT_SECONDS"]
        )
        purgable_events = []

        # Dismiss old events and count missing events as lost
        for event in probe.events.values():
            if now > event.time_sent + dismiss_event_timeout:
                if event.state == EventState.PENDING:
                    probe.metrics.events_lost.labels(probe.app_id).inc()

                purgable_events.append(event)

        for event in purgable_events:
            probe.events.pop(event.seqno, None)

        logger.info(f"Cleaned events, removed={len(purgable_events)}")


async def print_events(probe, interval):
    def since_prev_diff(event):
        previous_event = probe.events.get(event.seqno - 1)
        if not previous_event:
            return None
        return (event.time_sent - previous_event.time_sent).total_seconds()

    headers = ["#", "State", "TX", "RX", "Latency", "Age", "Diff. prev.", "Listener"]

    while True:
        await asyncio.sleep(interval)

        rows = [
            [
                seqno,
                e.state.upper(),
                e.time_sent,
                e.time_received,
                e.latency,
                e.since_sent.total_seconds(),
                since_prev_diff(e),
                id(e.received_by) if e.received_by else "",
            ]
            for seqno, e in probe.events.items()
        ]

        print(tabulate(rows, headers=headers))
