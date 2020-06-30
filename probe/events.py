from datetime import datetime, timezone
from itertools import count
from globals import app_id
from utils import log
from prometheus_client import Counter

counter = count(start=1)

events_posted_count = Counter(
    name="events_posted", documentation="Number of events posted"
)


def post_event(dataset_id, version, event_poster):
    event = {"app_id": app_id, "seqno": next(counter)}
    log.info(f"Sending event with ID {event['seqno']}")
    event["time_sent"] = datetime.now(timezone.utc).isoformat()

    event_poster.post_event(event, dataset_id, version)
    events_posted_count.inc()
