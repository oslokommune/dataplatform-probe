import logging
import os

from okdata.sdk.config import Config
from okdata.sdk.event.post_event import PostEvent

from .probe import Probe

LOCAL_RUN = os.getenv("LOCAL_RUN") == "true"
LOCAL_SERVICES_ONLY = os.getenv("LOCAL_SERVICES_ONLY") == "true"
LOCAL_EVENT_COLLECTOR_URL = "http://localhost:8081/"
WEBSOCKET_BASE_URL = (
    "ws://localhost:8765" if LOCAL_SERVICES_ONLY else os.environ["WEBSOCKET_URL"]
)

if LOCAL_RUN:
    import asyncio
    import json

    import coloredlogs
    import requests
    from tabulate import tabulate


def configure_logger():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    if LOCAL_RUN:
        coloredlogs.install(level="DEBUG", logger=logger)
        logging.getLogger("asyncio").setLevel(logging.ERROR)
        logging.getLogger("urllib3").setLevel(logging.ERROR)
        logging.getLogger("websockets").setLevel(logging.ERROR)

    return logger


def configure_sdk():
    if LOCAL_SERVICES_ONLY:

        class LocalSDK:
            def post_event(self, payload, dataset_id, version, retries):
                requests.post(LOCAL_EVENT_COLLECTOR_URL, json.dumps(payload))

        return LocalSDK()

    origo_config = Config()
    origo_config.config["cacheCredentials"] = True
    return PostEvent(config=origo_config)


async def print_events(probe, interval):
    def since_prev_diff(event):
        previous_event = probe.events.get(event.seqno - 1)
        if not previous_event:
            return None
        return (
            (event.time_sent - previous_event.time_sent).total_seconds()
        ) - probe.config["POST_EVENT_INTERVAL_SECONDS"]

    headers = ["#", "State", "TX", "RX", "Latency", "Age", "Diff. prev."]

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
            ]
            for seqno, e in probe.events.items()
        ]

        print(tabulate(rows, headers=headers))


if __name__ == "__main__":
    # Configure and run probe
    logger = configure_logger()
    sdk = configure_sdk()

    probe = Probe(
        sdk,
        {
            "POST_EVENT_INTERVAL_SECONDS": int(
                os.getenv("POST_EVENT_INTERVAL_SECONDS", 10)
            ),
            "MARK_EVENT_LOST_TIMEOUT_SECONDS": (5 * 60),
            "PURGE_EVENT_TIMEOUT_SECONDS": (15 * 60),
            "CLEAN_EVENTS_INTERVAL_SECONDS": int(
                os.getenv("CLEAN_EVENTS_INTERVAL_SECONDS", 30)
            ),
            "PROBE_DATASET_ID": os.environ["PROBE_DATASET_ID"],
            "PROBE_DATASET_VERSION": os.getenv("PROBE_DATASET_VERSION", 3),
            "WEBSOCKET_BASE_URL": WEBSOCKET_BASE_URL,
            "PROBE_WEBHOOK_TOKEN": os.environ["PROBE_WEBHOOK_TOKEN"],
        },
    )

    if LOCAL_RUN:
        probe.loop.create_task(print_events(probe, interval=30))

    probe.run()
