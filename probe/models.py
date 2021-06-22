from datetime import datetime, timedelta, timezone
from dataclasses import dataclass
from enum import Enum


class EventState(str, Enum):
    PENDING = "pending"
    RECEIVED = "received"
    ERROR = "error"


@dataclass
class Event:
    app_id: str
    seqno: int
    time_sent: datetime = None
    time_received: datetime = None
    state: EventState = None

    @property
    def latency(self):
        if self.time_received:
            return (self.time_received - self.time_sent).total_seconds()
        return None

    @property
    def since_sent(self) -> timedelta:
        if self.time_sent:
            return datetime.now(timezone.utc) - self.time_sent
        return None

    def __str__(self):
        return "{}_#{}_{}[{}]".format(
            self.app_id, self.seqno, hex(id(self)), self.state
        )
