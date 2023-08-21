import asyncio
import websockets
import json
import logging
import aioconsole

logging.basicConfig(level=logging.INFO)

async def test():
    uri = "ws://192.168.8.9:8765"
    async with websockets.connect(uri) as websocket:
        while True:
            try:
                message = await websocket.recv()
                data = json.loads(message)
                logging.info(data)

            except websockets.exceptions.ConnectionClosed:
                logging.error("Unreal Engine disconnected")
                break
            except Exception as e:
                logging.error(e)
                continue

            # Check for user input
            user_input = await aioconsole.ainput(">>> ")
            if user_input.strip().lower() == 'exit':
                break

asyncio.run(test())
