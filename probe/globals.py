import os
import uuid

event_interval = int(os.getenv("EVENT_INTERVAL_SECONDS"))
dataset_id = os.getenv("DATASET_ID")
app_id = str(uuid.uuid4())[:8]
