import asyncio
import logging
import websockets

CLIENTS = set()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def register(websocket):
    CLIENTS.add(websocket)


async def unregister(websocket):
    CLIENTS.remove(websocket)


async def send_all(event):
    logger.info(f"Sending event, clients={len(CLIENTS)}")
    for client in CLIENTS:
        try:
            await client.send(event)
        except Exception:
            pass


async def echo(websocket, path):
    await register(websocket)
    try:
        async for message in websocket:
            await send_all(message)
    finally:
        await unregister(websocket)


logger.info("Starting websocket server...")
start_server = websockets.serve(echo, "0.0.0.0", 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
