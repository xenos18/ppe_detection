import asyncio
import websockets


async def hello():
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        while True:
            greeting = await websocket.recv()
            print(f"<<< {greeting}")


if __name__ == "__main__":
    asyncio.run(hello())
