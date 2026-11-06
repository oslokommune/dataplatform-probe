import asyncio
import logging
from threading import Thread
from datetime import datetime, timedelta

import requests

from .models import RequestTask

logger = logging.getLogger(__name__)


def _token_url(config):
    return "{}/realms/{}/protocol/openid-connect/token".format(
        config["KEYCLOAK_SERVER_URL"].rstrip("/"), config["KEYCLOAK_REALM"]
    )


def _request_token(probe, request_task):
    """Request a new access token from Keycloak using client credentials.

    Keycloak is considered healthy when the token endpoint responds
    successfully with an access token.
    """
    config = probe.config
    url = _token_url(config)

    try:
        logger.debug(f"{request_task}: Requesting token from {url}")
        response = requests.post(
            url,
            data={
                "grant_type": "client_credentials",
                "client_id": config["KEYCLOAK_CLIENT_ID"],
                "client_secret": config["KEYCLOAK_CLIENT_SECRET"],
            },
            timeout=config["REQUEST_TIMEOUT_SECONDS"],
        )
        response.raise_for_status()
        if "access_token" not in response.json():
            raise ValueError("Token response did not contain an access token")
    except Exception as e:
        probe.on_request_task_fail(request_task, e)
    else:
        probe.on_request_task_success(request_task)

        if heartbeat_url := config["BETTERUPTIME_HEARTBEAT_URL"]:
            _send_heartbeat(heartbeat_url, config["REQUEST_TIMEOUT_SECONDS"])


def _send_heartbeat(url, timeout):
    try:
        logger.info("Heartbeat sent")
        response = requests.head(url, timeout=timeout)
        response.raise_for_status()
    except requests.RequestException as e:
        status_code = getattr(e.response, "status_code", None)
        logger.error(
            "Heartbeat request failed{}".format(
                f" ({status_code})" if status_code else ""
            )
        )


async def request_token(probe):
    interval = timedelta(seconds=int(probe.config["TASK_INTERVAL_SECONDS"]))
    next_request = datetime.now() + timedelta(seconds=2)

    while True:
        sleep_time = (next_request - datetime.now()).total_seconds()
        logger.debug(f"Sleeping {sleep_time} seconds")
        await asyncio.sleep(sleep_time)

        request_task = RequestTask(app_id=probe.app_id, seqno=next(probe.counter))
        probe.on_request_task_created(request_task)

        Thread(target=_request_token, args=(probe, request_task)).start()

        next_request = next_request + interval
