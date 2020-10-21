import threading
from time import sleep

from events import post_event
from globals import event_interval, max_consecutive_errors
from listener import listen_to_websocket
from utils import log, print_header

from requests import HTTPError

from aws_xray_sdk.core import xray_recorder
from origo.config import Config
from origo.event.post_event import PostEvent
from prometheus_client import start_http_server


def main():
    dataset_id = "monitoring-test"
    version = 1

    print_header()

    log.info("Getting requests session from client...")

    xray_recorder.begin_segment("Monitor")

    origo_config = Config()

    start_http_server(8000)
    log.info("Started prometheus server")

    origo_config.config["cacheCredentials"] = True
    event_poster = PostEvent(config=origo_config)

    listener = threading.Thread(
        target=listen_to_websocket, args=(dataset_id,), name="Listener", daemon=True
    )
    listener.start()

    log.info(
        f"Sending and listening to events continuously, sending every {event_interval} seconds"
    )
    num_of_errors = 0
    while True:
        if not listener.is_alive():
            log.info("Error encountered. Shutting down")
            break
        try:
            post_event(dataset_id, version, event_poster)
        except HTTPError as e:
            log.error(f"Exception ocurred when sending event: {e}")
            num_of_errors += 1
            if num_of_errors >= max_consecutive_errors:
                break
            continue
        num_of_errors = 0
        sleep(event_interval)

    listener.join()
    exit(1)


if __name__ == "__main__":
    main()
