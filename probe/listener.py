import json
import os
from datetime import datetime, timedelta, timezone

from prometheus_client import Counter, Gauge
from websocket import create_connection, WebSocketException

from events import events_posted, events_posted_lock
from globals import app_id, event_interval
from utils import log, EventPrinter, get_metric_name

webhook_token = os.getenv("WEBHOOK_TOKEN")
websocket_base_url = os.getenv("WEBSOCKET_URL")

received_event_count = Counter(
    name=get_metric_name("events_received"), documentation="Number of received events"
)

wrong_appid_count = Counter(
    name=get_metric_name("wrong_appid"),
    documentation="Number of events received with a mismatched app id",
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


printer = EventPrinter()


def update_missing_events():
    with events_posted_lock:
        timestamps = events_posted.values()

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


def _listen(ws, dataset_id):
    while True:
        update_missing_events()

        response = ws.recv()
        time_received = datetime.now(timezone.utc)

        if not response:
            raise WebSocketException("Unknown opcode from websocket `recv`.")

        result = json.loads(response)
        if result["app_id"] == app_id:
            seqno = result["seqno"]
            log.info(f"Received event with ID {seqno}")

            with events_posted_lock:
                events_posted.pop(seqno, None)
            update_missing_events()

            result["time_received"] = time_received.isoformat()
            result["time_spent"] = (
                time_received - datetime.fromisoformat(result["time_sent"])
            ).total_seconds()
            received_event_count.inc()
            printer.print_event(result)
        else:
            log.info(
                f"Received event with ID {seqno}, but app_id was not a match. Skipping"
            )
            wrong_appid_count.inc()


def listen_to_websocket(dataset_id):
    websocket_url = (
        f"{websocket_base_url}?dataset_id={dataset_id}&webhook_token={webhook_token}"
    )

    log.info(f"Attempting to listen to websocket at {websocket_base_url}")

    while True:
        try:
            log.info("Establishing connection to websocket...")
            ws = create_connection(websocket_url, timeout=event_interval + 60)
            _listen(ws, dataset_id)
        except WebSocketException as e:
            log.error(f"Exception received from websocket: {e}")
        finally:
            log.info("Closing the websocket")
            ws.close()
