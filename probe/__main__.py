import logging
import os

import requests
from okdata.sdk.data.dataset import Dataset

from .probe import Probe

LOCAL_RUN = os.getenv("LOCAL_RUN") == "true"
LOCAL_SERVICES_ONLY = os.getenv("LOCAL_SERVICES_ONLY") == "true"
LOCAL_API_URL = "http://localhost:8081"

if LOCAL_RUN:
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(levelname)-8s %(message)s",
    )
    logging.getLogger("asyncio").setLevel(logging.ERROR)
    logging.getLogger("urllib3").setLevel(logging.ERROR)
    logging.getLogger("websockets").setLevel(logging.ERROR)
else:
    logging.basicConfig(level=logging.INFO)


def configure_sdk():
    if LOCAL_SERVICES_ONLY:

        class LocalSDK:
            def get_dataset(self, datasetid, retries):
                res = requests.get(f"{LOCAL_API_URL}/metadata/{datasetid}")
                res.raise_for_status()
                return res.json()

        return LocalSDK()

    return Dataset()


if __name__ == "__main__":
    # Configure and run probe
    sdk = configure_sdk()

    probe = Probe(
        sdk,
        {
            "BETTERUPTIME_HEARTBEAT_URL": os.getenv("BETTERUPTIME_HEARTBEAT_URL"),
            "DATASET_ID": os.environ["DATASET_ID"],
            "TASK_INTERVAL_SECONDS": int(os.getenv("TASK_INTERVAL_SECONDS", 30)),
        },
    )

    probe.run()
