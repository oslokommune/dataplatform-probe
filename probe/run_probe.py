import threading
from time import sleep

from events import post_event
from globals import event_interval
from listener import listen_to_websocket
from receiver import get_returned_events
from utils import log, print_header

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

    receiver = threading.Thread(
        target=get_returned_events, name="Receiver", daemon=True
    )
    receiver.start()

    log.info(
        f"Sending and listening to events continuously, sending every {event_interval} seconds"
    )

    while True:
        post_event(dataset_id, version, event_poster)
        sleep(event_interval)


if __name__ == "__main__":
    main()
