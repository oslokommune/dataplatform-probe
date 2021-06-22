import asyncio
import json
import logging
import uuid
from datetime import datetime, timedelta, timezone
from itertools import count

import websockets
from prometheus_client import start_http_server

from .metrics import Metrics
from .models import Event, EventState
from .tasks import clean_events, post_event

logger = logging.getLogger(__name__)


class Probe(object):
    def __init__(self, sdk, config):
        logger.info("Initializing probe application")

        self.app_id = str(uuid.uuid4())[:8]
        self.config = config
        self.sdk = sdk
        self.counter = count(start=1)
        self.events = {}
        self.metrics = Metrics()
        self.loop = asyncio.get_event_loop()

    def on_event_post(self, event: Event):
        event.time_sent = datetime.now(timezone.utc)
        event.state = EventState.PENDING
        self.events[event.seqno] = event
        logger.info(f"Event TX: {event}")

    def on_event_posted(self, event: Event):
        self.metrics.events_posted.inc()

    def on_event_post_error(self, event: Event):
        event.state = EventState.ERROR
        logger.error(f"Event TX failed: {event}")
        self.metrics.event_post_errors.inc()

    def on_event_received(self, event_data: str):
        now = datetime.now(timezone.utc)
        event_data = json.loads(event_data)

        if event_data["app_id"] != self.app_id:
            logger.warning(
                "Received event with ID {}, but app_id ({}) was not a match. Skipping!".format(
                    event_data["seqno"], event_data["app_id"]
                )
            )
            self.metrics.wrong_appid_count.inc()
            return

        event = self.events.get(event_data["seqno"])

        if not event:
            logger.warning(
                "Unknown event with ID {} received".format(event_data["seqno"])
            )
            # TODO: Count it?
            return

        # Count duplicated events
        if event.state == EventState.RECEIVED:
            self.metrics.events_duplicates.inc()

        event.time_received = now
        event.state = EventState.RECEIVED
        logger.info(f"Event RX: {event} (latency={event.latency})")
        self.metrics.event_latency.set(event.latency)
        self.metrics.events_received.inc()

        # Update state for tracked events
        self.update_event_states()

    def update_event_states(self):
        now = datetime.now(timezone.utc)
        consider_lost_timeout = timedelta(
            seconds=self.config["MARK_EVENT_LOST_TIMEOUT_SECONDS"]
        )
        purgable_timeout = timedelta(seconds=self.config["PURGE_EVENT_TIMEOUT_SECONDS"])

        for event in self.events.values():
            if (event.state == EventState.PENDING) and (
                now > (event.time_sent + consider_lost_timeout)
            ):
                event.state = EventState.LOST
                self.metrics.events_lost.inc()

            if now > event.time_sent + purgable_timeout:
                event.state = EventState.PURGABLE

        # Update metrics for missing events
        for metric_attr, timestamp in (
            ("events_missing_1m_share", (now - timedelta(minutes=1))),
            ("events_missing_3m_share", (now - timedelta(minutes=3))),
            ("events_missing_10m_share", (now - timedelta(minutes=10))),
        ):
            events = self.get_events_sent_after(timestamp)
            missing_events = [e for e in events if e.state != EventState.RECEIVED]
            share_of_events_missing = len(missing_events) / len(events) * 100
            metric = getattr(self.metrics, metric_attr)
            metric.set(share_of_events_missing)

    def get_events_sent_after(self, timestamp):
        return [e for e in self.events.values() if e.time_sent > timestamp]

    async def listener(self):
        websocket_uri = "{}?dataset_id={}&webhook_token={}".format(
            self.config["WEBSOCKET_BASE_URL"],
            self.config["PROBE_DATASET_ID"],
            self.config["PROBE_WEBHOOK_TOKEN"],
        )

        while True:
            try:
                logger.info(f"Connecting to {websocket_uri}")
                async with websockets.connect(websocket_uri) as websocket:
                    logger.info("Connected to websocket endpoint")
                    while True:
                        response = await websocket.recv()
                        self.on_event_received(response)
            except websockets.exceptions.WebSocketException as e:
                logger.error(f"Exception received from websocket: {e}")
                logger.info("Connection closed")

    def run(self):
        logger.info("Running probe")

        # Serve Prometheus metrics
        start_http_server(8000)

        self.loop.create_task(post_event(self))
        self.loop.create_task(clean_events(self))

        self.loop.run_until_complete(self.listener())
