from datetime import datetime
from dataclasses import dataclass
from enum import Enum


class RequestState(str, Enum):
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


@dataclass
class RequestTask:
    app_id: str
    seqno: int
    time_created: datetime = None
    time_succeeded: datetime = None
    time_failed: datetime = None
    state: RequestState = None

    @property
    def duration(self):
        time_completed = self.time_succeeded or self.time_failed
        if time_completed:
            return (time_completed - self.time_created).total_seconds()
        return None

    def __str__(self):
        return "{}_#{}_{}[{}]".format(
            self.app_id, self.seqno, hex(id(self)), self.state
        )
