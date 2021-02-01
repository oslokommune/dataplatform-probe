import json
from datetime import datetime, timezone

import websockets
from prometheus_client import Counter

from events import mark_event_as_seen
from globals import app_id
from utils import log, EventPrinter, get_metric_name

received_event_count = Counter(
    name=get_metric_name("events_received"), documentation="Number of received events"
)

wrong_appid_count = Counter(
    name=get_metric_name("wrong_appid"),
    documentation="Number of events received with a mismatched app id",
)

printer = EventPrinter()


async def _listen(websocket):
    while True:
        response = await websocket.recv()
        time_received = datetime.now(timezone.utc)

        result = json.loads(response)
        seqno = result["seqno"]

        if result["app_id"] == app_id:
            log.info(f"Received event with ID {seqno}")

            mark_event_as_seen(seqno)

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


async def listen_to_websocket(uri):
    log.info(f"Attempting to listen to websocket at {uri}")

    while True:
        try:
            log.info("Establishing connection to websocket...")
            async with websockets.connect(uri) as websocket:
                log.info("Connection established")
                await _listen(websocket)
        except websockets.exceptions.WebSocketException as e:
            log.error(f"Exception received from websocket: {e}")
            log.info("Connection closed")
