import os
import uuid

event_interval = int(os.getenv("EVENT_INTERVAL_SECONDS"))
max_consecutive_errors = int(os.getenv("MAX_CONSECUTIVE_ERRORS"))
dataset_id = os.getenv("DATASET_ID")
app_id = str(uuid.uuid4())[:8]
