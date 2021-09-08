import asyncio
import logging

from websockets import connect as websocket_connect
from websockets.exceptions import WebSocketException

logger = logging.getLogger(__name__)


class Listener:
    """WebSocket client for receiving probe events.

    Connect to the specified `websocket_uri` and pass all received
    events to the parent `probe` application instance. Delay first
    (re)connect if `delay_start` is specified.
    """

    def __init__(
        self,
        probe,
        listener_id,
        websockets_uri,
        delay_start=0,
    ):
        self.probe = probe
        self.id = listener_id
        self.uri = websockets_uri
        self.delay = delay_start

        logger.info(f"Initialized listener #{self.id} (delay={self.delay})")

    async def start(self):
        attempts = 0
        backoff_factor = 0.5
        max_connection_attempts = 10

        while True:
            if attempts == 0 and self.delay > 0:
                # Induce additional delay on first (re-)connect for additional
                # listener in order to prevent listeners from starting at the
                # same time.
                await asyncio.sleep(self.delay)

            try:
                attempts += 1
                logger.info(f"{self}: Connecting to {self.uri}, attempt={attempts}")
                async with websocket_connect(self.uri) as websocket:
                    logger.info(f"{self}: Connected to websocket endpoint")
                    attempts = 0

                    while True:
                        response = await websocket.recv()
                        self.probe.on_event_received(response, self)
            except WebSocketException as e:
                logger.error(f"{self}: Exception received from websocket: {e}")
                logger.info(f"{self}: Connection closed")
            except OSError as e:
                # Treat as retriable (?)
                #  https://github.com/aaugustin/websockets/issues/593
                #  https://bugs.python.org/issue29980
                logger.error(f"{self}: Connection failed: {e}")

            await asyncio.sleep(backoff_factor * attempts)

            if attempts == max_connection_attempts:
                logger.warning(f"{self}: Exhausted all connection retry attempts")
                break

    def __str__(self):
        return f"Listener#{self.id}"
