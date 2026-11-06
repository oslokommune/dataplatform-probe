import logging
import os

from .probe import Probe

LOCAL_RUN = os.getenv("LOCAL_RUN") == "true"

if LOCAL_RUN:
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(levelname)-8s %(message)s",
    )
    logging.getLogger("asyncio").setLevel(logging.ERROR)
    logging.getLogger("urllib3").setLevel(logging.ERROR)
else:
    logging.basicConfig(level=logging.INFO)


if __name__ == "__main__":
    # Configure and run probe
    probe = Probe(
        {
            "BETTERUPTIME_HEARTBEAT_URL": os.getenv("BETTERUPTIME_HEARTBEAT_URL"),
            "KEYCLOAK_SERVER_URL": os.environ["KEYCLOAK_SERVER_URL"],
            "KEYCLOAK_REALM": os.environ["KEYCLOAK_REALM"],
            "KEYCLOAK_CLIENT_ID": os.environ["KEYCLOAK_CLIENT_ID"],
            "KEYCLOAK_CLIENT_SECRET": os.environ["KEYCLOAK_CLIENT_SECRET"],
            "REQUEST_TIMEOUT_SECONDS": int(os.getenv("REQUEST_TIMEOUT_SECONDS", 10)),
            "TASK_INTERVAL_SECONDS": int(os.getenv("TASK_INTERVAL_SECONDS", 30)),
        },
    )

    probe.run()
