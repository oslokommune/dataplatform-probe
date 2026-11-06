import time
import random
import logging

from flask import Flask, jsonify, request

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


@app.route("/realms/<realm>/protocol/openid-connect/token", methods=["POST"])
def token(realm):
    """Emulate the Keycloak token endpoint for the client credentials grant."""
    if prc(percent=CONFIG["ADD_LATENCY_PERCENT"]):
        sleep = random.uniform(CONFIG["LATENCY_RANGE_MIN"], CONFIG["LATENCY_RANGE_MAX"])
        logger.warning(f"Introducing latency, sleeping {sleep}")
        time.sleep(sleep)

    if request.form.get("grant_type") != "client_credentials":
        return jsonify({"error": "unsupported_grant_type"}), 400

    if prc(percent=CONFIG["NOT_AUTHORIZED_PERCENT"]):
        return (
            jsonify(
                {
                    "error": "invalid_client",
                    "error_description": "Invalid client or Invalid client credentials",
                }
            ),
            401,
        )

    return jsonify(
        {
            "access_token": f"dummy-token-for-{realm}",
            "expires_in": 300,
            "token_type": "Bearer",
        }
    )


@app.route("/heartbeat")
def heartbeat():
    logger.info("Heartbeat received")
    return "OK", 200


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8081)
