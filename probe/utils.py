from datetime import datetime
from logging import getLogger, Formatter, StreamHandler, getLevelName

from prometheus_client import Gauge

log = getLogger()
log.setLevel(getLevelName("INFO"))
log_formatter = Formatter("%(threadName)s -[%(levelname)s]: %(message)s")
handler = StreamHandler()
handler.setFormatter(log_formatter)
log.addHandler(handler)


def get_metric_name(name):
    return f"probe_{name}"


def print_header():
    with open("resources/header.txt", "r") as f:
        print(f.read())


class EventPrinter:
    event_latency = Gauge(
        name=get_metric_name("event_latency"), documentation="Event latency"
    )

    def print_event(self, event):
        log.info(
            f"Event Id: {event['seqno']} - Time Sent: {datetime.fromisoformat(event['time_sent'])} "
            f"- Time Received: {datetime.fromisoformat(event['time_received'])} "
            f"- Time Spent(seconds): {event['time_spent']}"
        )
        self.event_latency.set(event["time_spent"])
