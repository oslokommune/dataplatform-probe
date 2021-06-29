import json
import logging
import os

import requests
from okdata.sdk.config import Config
from okdata.sdk.event.post_event import PostEvent

from .probe import Probe
from .tasks import print_events

LOCAL_RUN = os.getenv("LOCAL_RUN") == "true"
LOCAL_SERVICES_ONLY = os.getenv("LOCAL_SERVICES_ONLY") == "true"
LOCAL_EVENT_COLLECTOR_URL = "http://localhost:8081/"
WEBSOCKET_BASE_URL = (
    "ws://localhost:8765" if LOCAL_SERVICES_ONLY else os.environ["WEBSOCKET_URL"]
)


def configure_logger():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    if LOCAL_RUN:
        logger.setLevel(level=logging.DEBUG)
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


if __name__ == "__main__":
    # Configure and run probe
    logger = configure_logger()
    sdk = configure_sdk()

    probe = Probe(
        sdk,
        {
            "EVENT_INTERVAL_SECONDS": int(os.getenv("EVENT_INTERVAL_SECONDS", 10)),
            "DISMISS_EVENT_TIMEOUT_SECONDS": int(
                os.getenv("DISMISS_EVENT_TIMEOUT_SECONDS", 60 * 60 * 24)
            ),
            "CLEAN_EVENTS_INTERVAL_SECONDS": int(
                os.getenv("CLEAN_EVENTS_INTERVAL_SECONDS", 60 * 5)
            ),
            "DATASET_ID": os.environ["DATASET_ID"],
            "DATASET_VERSION": os.getenv("DATASET_VERSION", 1),
            "WEBSOCKET_BASE_URL": WEBSOCKET_BASE_URL,
            "WEBHOOK_TOKEN": os.environ["WEBHOOK_TOKEN"],
        },
    )

    if LOCAL_RUN:
        probe.loop.create_task(print_events(probe, interval=30))

    probe.run()
