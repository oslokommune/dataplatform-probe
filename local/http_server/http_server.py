import time
import random
import logging

from flask import Flask, jsonify


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CONFIG = {
    "ADD_LATENCY_PERCENT": 10,
    "LATENCY_RANGE_MIN": 0,
    "LATENCY_RANGE_MAX": 3,
    "NOT_AUTHORIZED_PERCENT": 5,
}

app = Flask(__name__)


def prc(percent=10):
    return random.randrange(100) < percent


@app.route("/metadata/<dataset_id>")
def get_dataset_metadata(dataset_id):
    if prc(percent=CONFIG["ADD_LATENCY_PERCENT"]):
        sleep = random.uniform(CONFIG["LATENCY_RANGE_MIN"], CONFIG["LATENCY_RANGE_MAX"])
        logger.warning(f"Introducing latency, sleeping {sleep}")
        time.sleep(sleep)

    if prc(percent=CONFIG["NOT_AUTHORIZED_PERCENT"]):
        return jsonify({"message": "Unauthorized"}), 401

    return jsonify(
        {
            "Type": "Dataset",
            "Id": dataset_id,
            "title": "Probe",
        }
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8081)
