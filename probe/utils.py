from datetime import datetime
from logging import getLogger, Formatter, StreamHandler, getLevelName
from math import inf
from prometheus_client import Gauge

log = getLogger()
log.setLevel(getLevelName("INFO"))
log_formatter = Formatter("%(threadName)s -[%(levelname)s]: %(message)s")
handler = StreamHandler()
handler.setFormatter(log_formatter)
log.addHandler(handler)


def print_header():
    with open("resources/header.txt", "r") as f:
        print(f.read())


class EventPrinter:
    max_time_spent = -inf
    min_time_spent = inf
    avg_time_spent = 0.0
    events_received = 0
    max_time_spent_gauge = Gauge(
        name="max_time_spent", documentation="Maximum event latency"
    )
    min_time_spent_gauge = Gauge(
        name="min_time_spent", documentation="Minimum event latency"
    )
    avg_time_spent_gauge = Gauge(
        name="avg_time_spent", documentation="Average event latency"
    )

    def print_event(self, event):
        log.info(
            f"Event Id: {event['seqno']} - Time Sent: {datetime.fromisoformat(event['time_sent'])} "
            f"- Time Received: {datetime.fromisoformat(event['time_received'])} "
            f"- Time Spent(seconds): {event['time_spent']}"
        )

        self.events_received += 1
        self.max_time_spent = max(self.max_time_spent, event["time_spent"])
        self.min_time_spent = min(self.min_time_spent, event["time_spent"])
        self.avg_time_spent = self.avg_time_spent + (
            (event["time_spent"] - self.avg_time_spent) / self.events_received
        )
        self.max_time_spent_gauge.set(self.max_time_spent)
        self.min_time_spent_gauge.set(self.min_time_spent)
        self.avg_time_spent_gauge.set(self.avg_time_spent)
        log.info(f"Max time spent: {round(self.max_time_spent, 2)}s")
        log.info(f"Min time spent: {round(self.min_time_spent, 2)}s")
        log.info(f"Average time spent: {round(self.avg_time_spent, 2)}s")

        # t = PrettyTable(["Event ID", 'Time Sent', "Time Received", "Time spent(seconds)"])
        # for event in events_to_print:
        #    t.add_row(
        #        [event['seqno'], datetime.fromisoformat(event['time_sent']),
        #         datetime.fromisoformat(event['time_received']), event['time_spent']]
        #    )
        # log.info(f"Printing {len(events_to_print)} events")
        # log.info("\n" + str(t))

        # time_spent_values = [event['time_spent'] for event in events_to_print]
        # log.info(f"Max time spent: {round(max(time_spent_values), 2)}s")
        # log.info(f"Min time spent: {round(min(time_spent_values), 2)}s")
        # log.info(f"Average time spent: {round(sum(time_spent_values) / len(time_spent_values), 2)}s")
