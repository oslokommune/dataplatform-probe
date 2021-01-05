from datetime import datetime, timedelta, timezone
from itertools import count
from threading import RLock

from prometheus_client import Counter, Gauge

from globals import app_id
from utils import log, get_metric_name

_counter = count(start=1)

event_post_count = Counter(
    name=get_metric_name("events_posted"), documentation="Number of events posted"
)

event_post_error_count = Counter(
    name=get_metric_name("event_post_errors"),
    documentation="Number of errors that occurred while posting events",
)

events_missing_10s = Gauge(
    name=get_metric_name("events_missing_10s"),
    documentation="Number of missing events that are less than 10 seconds old",
)

events_missing_1m = Gauge(
    name=get_metric_name("events_missing_1m"),
    documentation="Number of missing events that are less than 1 minute old",
)

events_missing_10m = Gauge(
    name=get_metric_name("events_missing_10m"),
    documentation="Number of missing events that are less than 10 minutes old",
)

events_missing_1h = Gauge(
    name=get_metric_name("events_missing_1h"),
    documentation="Number of missing events that are less than 1 hour old",
)

_events_posted_lock = RLock()
_events_posted = {}


def _update_missing_events():
    timestamps = _events_posted.values()
    now = datetime.now(timezone.utc)

    events_missing_10s.set(
        sum(1 for ts in timestamps if ts > now - timedelta(seconds=10))
    )
    events_missing_1m.set(
        sum(1 for ts in timestamps if ts > now - timedelta(minutes=1))
    )
    events_missing_10m.set(
        sum(1 for ts in timestamps if ts > now - timedelta(minutes=10))
    )
    events_missing_1h.set(
        sum(1 for ts in timestamps if ts > now - timedelta(minutes=60))
    )


def mark_event_as_seen(seqno):
    with _events_posted_lock:
        _events_posted.pop(seqno, None)
        _update_missing_events()


def post_event(dataset_id, version, event_poster):
    seqno = next(_counter)
    now = datetime.now(timezone.utc)
    event = {"app_id": app_id, "seqno": seqno, "time_sent": now.isoformat()}
    log.info(f"Sending event with ID {seqno}")

    try:
        event_poster.post_event(event, dataset_id, version)
        event_post_count.inc()

        with _events_posted_lock:
            _events_posted[seqno] = now
            _update_missing_events()

    except Exception as e:
        log.error(f"Error when sending event: {e}")
        event_post_error_count.inc()
