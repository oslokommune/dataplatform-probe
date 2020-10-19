from globals import received_events
from utils import EventPrinter, log

printer = EventPrinter()


def get_returned_events():
    log.info("Waiting for events")
    while True:
        event = received_events.get()
        log.info("Found event, printing")
        printer.print_event(event)
