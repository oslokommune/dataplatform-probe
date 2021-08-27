import asyncio
import logging
import websockets

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

listeners = []


async def disturbinator(interval):
    """ Close the oldest listener every n seconds. """
    while True:
        await asyncio.sleep(interval)
        if listeners:
            listener = listeners.pop()
            await listener.close(code=1001, reason="Going away")
            logger.info(f"Closed a listener, {len(listeners)} left")


async def dispatcher(websocket, path):
    if "dataset_id" in path:
        # Probe event listener
        listeners.insert(0, websocket)
        logger.info(f"Listener connected, total={len(listeners)}")

    try:
        async for message in websocket:
            if listeners:
                # Broadcast event to all connected listeners
                logger.info(f"Sending event (listeners={len(listeners)})")
                await asyncio.wait([l.send(message) for l in listeners])
            else:
                logger.warning("Ignoring event, no one listening..")
    except websockets.exceptions.ConnectionClosedError:
        if websocket in listeners:
            listeners.remove(websocket)
            logger.info(f"Listener disconnected, total={len(listeners)}")


logger.info("Starting websocket server...")
start_server = websockets.serve(dispatcher, "0.0.0.0", 8765)

loop = asyncio.get_event_loop()
loop.create_task(disturbinator(180))
loop.run_until_complete(start_server)
loop.run_forever()
