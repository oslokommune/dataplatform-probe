import json
import time
import random
import logging

from flask import Flask, request, jsonify
from websocket import create_connection


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

WS_URI = "ws://wsserver:8765"
CONFIG = {
    "ADD_LATENCY_PERCENT": 10,
    "LATENCY_RANGE_MIN": 0,
    "LATENCY_RANGE_MAX": 3,
    "NO_EMIT_PERCENT": 5,
}

app = Flask(__name__)


def prc(percent=10):
    return random.randrange(100) < percent


@app.route("/", methods=["POST"])
def event_collector():
    event = json.loads(request.data)
    logger.info(f"Event received: {event}")

    if prc(percent=CONFIG["ADD_LATENCY_PERCENT"]):
        sleep = random.uniform(CONFIG["LATENCY_RANGE_MIN"], CONFIG["LATENCY_RANGE_MAX"])
        logger.warning(f"Introducing latency, sleeping {sleep}")
        time.sleep(sleep)

    if prc(percent=CONFIG["NO_EMIT_PERCENT"]):
        logger.warning("No emit for this event")
    else:
        ws = create_connection(WS_URI)
        ws.send(json.dumps(event))
        ws.close()

    return jsonify({"seqno": event["seqno"]})


@app.route("/config/", methods=["GET"])
def config():
    args = request.args
    if "ADD_LATENCY_PERCENT" in args:
        percentage = int(args["ADD_LATENCY_PERCENT"])
        if percentage >= 0 and percentage <= 100:
            CONFIG["ADD_LATENCY_PERCENT"] = percentage
    for arg in ["LATENCY_RANGE_MIN", "LATENCY_RANGE_MAX"]:
        if arg in args and int(args[arg]) > 0:
            CONFIG[arg] = int(args[arg])
    if "NO_EMIT_PERCENT" in args:
        percentage = int(args["NO_EMIT_PERCENT"])
        if percentage >= 0 and percentage <= 100:
            CONFIG["NO_EMIT_PERCENT"] = percentage
    return jsonify(CONFIG)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8081)
