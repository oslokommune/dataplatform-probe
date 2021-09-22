import asyncio
import json
import logging
import uuid
from datetime import datetime, timedelta, timezone
from itertools import count

from prometheus_client import start_http_server

from .listener import Listener
from .metrics import Metrics
from .models import Event, EventState
from .tasks import clean_events, post_event

logger = logging.getLogger(__name__)


class Probe:
    def __init__(self, sdk, config):
        logger.info("Initializing probe application")

        self.app_id = str(uuid.uuid4())[:8]
        self.config = config
        self.sdk = sdk
        self.counter = count(start=1)
        self.events = {}
        self.metrics = Metrics()
        self.listeners = [
            Listener(
                probe=self,
                websockets_uri="{}?dataset_id={}&webhook_token={}".format(
                    self.config["WEBSOCKET_BASE_URL"],
                    self.config["DATASET_ID"],
                    self.config["WEBHOOK_TOKEN"],
                ),
                delay_start=(i * 15),
            )
            for i in range(self.config["WEBSOCKET_LISTENERS"])
        ]
        self.loop = asyncio.get_event_loop()

    def on_event_post(self, event: Event):
        event.time_sent = datetime.now(timezone.utc)
        event.state = EventState.PENDING
        self.events[event.seqno] = event
        logger.info(f"Event TX: {event}")

    def on_event_posted(self, event: Event):
        self.metrics.events_posted.labels(self.app_id).inc()

    def on_event_post_error(self, event: Event):
        event.state = EventState.ERROR
        logger.error(f"Event TX failed: {event}")
        self.metrics.event_post_errors.labels(self.app_id).inc()

    def on_event_received(self, event_data: str, listener: Listener):
        now = datetime.now(timezone.utc)
        event_data = json.loads(event_data)

        if event_data["app_id"] != self.app_id:
            logger.warning(
                "{} received event with ID {}, but app_id ({}) was not a match. Skipping!".format(
                    listener, event_data["seqno"], event_data["app_id"]
                )
            )
            self.metrics.wrong_appid_count.labels(self.app_id).inc()
            return

        event = self.events.get(event_data["seqno"])

        if not event:
            logger.warning(
                "{} received unknown event with ID {}".format(
                    listener, event_data["seqno"]
                )
            )
            # TODO: Count it?
            return

        # Check for duplicated events
        if event.state == EventState.RECEIVED:
            # Ignore events previously received by another handler
            if event.received_by != listener:
                logger.debug(
                    "Ignoring event {} from {} (already received by {})".format(
                        event, listener, event.received_by
                    )
                )
                return

            self.metrics.events_duplicates.labels(self.app_id).inc()

        event.time_received = now
        event.state = EventState.RECEIVED
        event.received_by = listener
        logger.info(
            "Event RX: {} (latency={}, listener={})".format(
                event, event.latency, listener
            )
        )
        self.metrics.event_latency.set(event.latency)
        self.metrics.events_received.labels(self.app_id).inc()

        # Update state for tracked events
        self.update_event_states()

    def update_event_states(self):
        now = datetime.now(timezone.utc)

        # Update metrics for missing events
        for metric_attr, timestamp in (
            ("events_missing_1m_share", (now - timedelta(minutes=1))),
            ("events_missing_10m_share", (now - timedelta(minutes=10))),
            ("events_missing_1h_share", (now - timedelta(hours=1))),
        ):
            events = self.get_events_sent_after(timestamp)
            sent_events = [e for e in events if e.state != EventState.ERROR]
            missing_events = [e for e in sent_events if e.state == EventState.PENDING]
            share_of_events_missing = (
                len(missing_events) / len(sent_events) * 100 if sent_events else 0.0
            )
            metric = getattr(self.metrics, metric_attr)
            metric.set(share_of_events_missing)

    def get_events_sent_after(self, timestamp):
        return [e for e in self.events.values() if e.time_sent > timestamp]

    def run(self):
        logger.info("Running probe")

        # Serve Prometheus metrics
        start_http_server(8000)

        self.loop.create_task(post_event(self))
        self.loop.create_task(clean_events(self))

        self.loop.run_until_complete(
            asyncio.wait([listener.start() for listener in self.listeners])
        )
