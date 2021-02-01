import asyncio
import os
import threading

from aws_xray_sdk.core import xray_recorder
from okdata.sdk.config import Config
from okdata.sdk.event.post_event import PostEvent
from prometheus_client import start_http_server

from events import post_event
from globals import event_interval
from listener import listen_to_websocket
from utils import log, print_header

webhook_token = os.getenv("WEBHOOK_TOKEN")
websocket_base_url = os.getenv("WEBSOCKET_URL")


def main():
    dataset_id = os.getenv("DATASET_ID")
    version = 1

    print_header()

    log.info("Getting requests session from client...")

    xray_recorder.begin_segment("Monitor")

    origo_config = Config()

    start_http_server(8000)
    log.info("Started prometheus server")

    origo_config.config["cacheCredentials"] = True
    event_poster = PostEvent(config=origo_config)

    def _post_event():
        threading.Timer(event_interval, _post_event).start()
        post_event(dataset_id, version, event_poster)

    _post_event()

    websocket_uri = (
        f"{websocket_base_url}?dataset_id={dataset_id}&webhook_token={webhook_token}"
    )
    asyncio.get_event_loop().run_until_complete(listen_to_websocket(websocket_uri))

    log.info(
        f"Sending and listening to events continuously, sending every {event_interval} seconds"
    )

    exit(1)


if __name__ == "__main__":
    main()
