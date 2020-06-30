import os
import uuid
from queue import Queue

event_interval = int(os.getenv("EVENT_INTERVAL_SECONDS"))
received_events = Queue()
app_id = str(uuid.uuid4())[:8]
