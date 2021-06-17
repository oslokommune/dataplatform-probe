import asyncio
import logging
from threading import Thread
from datetime import datetime, timedelta, timezone

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
            probe.config["PROBE_DATASET_ID"],
            probe.config["PROBE_DATASET_VERSION"],
            retries=3,
        )

    except Exception as e:
        logger.error(f"Event emit failed: event={event}, err={e}")
        probe.on_event_post_error(event)
    else:
        logger.debug(f"Event posted: {event}")
        probe.on_event_posted(event)


async def post_event(probe):
    drift = timedelta()
    interval = int(probe.config["POST_EVENT_INTERVAL_SECONDS"])

    while True:
        # Create new event
        event = Event(app_id=probe.app_id, seqno=next(probe.counter))
        previous_event = probe.events.get((event.seqno - 1))
        now = datetime.now(timezone.utc)
        sleep_time = interval

        if previous_event:
            previous_sent = previous_event.time_sent
            drift = now - previous_sent
            logger.debug(f"Diff previous: {drift}")
            sleep_time = interval - drift.microseconds / 1000000.0

        await asyncio.sleep(sleep_time)

        probe.on_event_post(event)
        Thread(target=_post_request, args=(probe, event)).start()

        logger.debug(
            "Periodic event emit, drift={}, slept={}".format(drift, sleep_time)
        )


async def clean_events(probe):
    interval = int(probe.config["CLEAN_EVENTS_INTERVAL_SECONDS"])

    while True:
        await asyncio.sleep(interval)

        # Purge old events
        purgable_events = [
            e for e in probe.events.values() if e.state == EventState.PURGABLE
        ]

        for event in purgable_events:
            probe.events.pop(event.seqno, None)

        logger.info(f"Cleaned events, removed={len(purgable_events)}")
