from datetime import datetime, timezone
from itertools import count
from threading import RLock

from prometheus_client import Counter
from requests import HTTPError

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

events_posted_lock = RLock()
events_posted = {}


def post_event(dataset_id, version, event_poster):
    seqno = next(_counter)
    now = datetime.now(timezone.utc)
    event = {"app_id": app_id, "seqno": seqno, "time_sent": now.isoformat()}
    log.info(f"Sending event with ID {seqno}")

    try:
        event_poster.post_event(event, dataset_id, version)
        with events_posted_lock:
            events_posted[seqno] = now

    except HTTPError as e:
        log.error(f"Error when sending event: {e}")
        event_post_error_count.inc()

    event_post_count.inc()
