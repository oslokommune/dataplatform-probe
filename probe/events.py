from datetime import datetime, timezone
from itertools import count

from prometheus_client import Counter
from requests import HTTPError

from globals import app_id
from utils import log, get_metric_name

counter = count(start=1)

event_post_count = Counter(
    name=get_metric_name("events_posted"), documentation="Number of events posted"
)

event_post_error_count = Counter(
    name=get_metric_name("event_post_errors"),
    documentation="Number of errors that occurred while posting events",
)


def post_event(dataset_id, version, event_poster):
    event = {"app_id": app_id, "seqno": next(counter)}
    log.info(f"Sending event with ID {event['seqno']}")
    event["time_sent"] = datetime.now(timezone.utc).isoformat()

    try:
        event_poster.post_event(event, dataset_id, version)
    except HTTPError as e:
        log.error(f"Error when sending event: {e}")
        event_post_error_count.inc()

    event_post_count.inc()
