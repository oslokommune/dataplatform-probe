import os
import uuid

event_interval = int(os.getenv("EVENT_INTERVAL_SECONDS"))
app_id = str(uuid.uuid4())[:8]
