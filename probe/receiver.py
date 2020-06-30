from globals import received_events
from utils import EventPrinter

printer = EventPrinter()


def get_returned_events():
    while True:
        event = received_events.get()
        printer.print_event(event)
