import json
import os
from datetime import datetime, timezone

from globals import received_events, app_id
from utils import log
from websocket import create_connection, WebSocketException
from prometheus_client import Counter

webhook_token = os.getenv("WEBHOOK_TOKEN")
websocket_base_url = os.getenv("WEBSOCKET_URL")

received_event_count = Counter(
    name="events_received", documentation="Number of received events"
)
wrong_appid_count = Counter(
    name="wrong_appid",
    documentation="Number of events received with a mismatched app id",
)


def listen_to_websocket(dataset_id):
    websocket_url = (
        f"{websocket_base_url}?dataset_id={dataset_id}&webhook_token={webhook_token}"
    )

    log.info(f"Attempting to listen to websocket at {websocket_base_url}")
    try:
        log.info("Establishing connection to websocket...")
        ws = create_connection(websocket_url)
        while True:
            result = ws.recv()
            result_json = json.loads(result)
            if result_json["app_id"] == app_id:
                log.info(f"Received event with ID {result_json['seqno']}")
                time_received = datetime.now(timezone.utc)
                result_json["time_received"] = time_received.isoformat()
                result_json["time_spent"] = (
                    time_received - datetime.fromisoformat(result_json["time_sent"])
                ).total_seconds()
                received_event_count.inc()
                received_events.put(result_json)
            else:
                log.info(
                    f"Received event with ID {result_json['seqno']}, but app_id was not a match. Skipping"
                )
                wrong_appid_count.inc()
    except WebSocketException as e:
        log.error(f"Exception received from websocket: {e}")
        pass

    ws.close()
