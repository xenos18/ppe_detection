import random

import uvicorn
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict
from multiprocessing import Process, Manager, Value

from video import camera
from routers import admin
import asyncio

# from bot.main import *

app = FastAPI()
app.include_router(admin.router)
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
manager: Manager
image: Value
results: Value

ws_dict: Dict[int, WebSocket] = {}


async def send():
    while True:
        print(1)
        for ws_id in ws_dict.keys():
            ws = ws_dict[ws_id]
            if image.value is None:
                continue
            print('Step two')

            await ws.send_bytes(image.value)
            await ws.send_json({
                "type": "detection",
                "ok": True,
                "humans": results.value
            })

        await asyncio.sleep(0.1)


def start():
    x = Process(target=camera, args=(image, results))
    x.start()

    # Process(target=start_bot, args=(image, )).start()
    print('start_as')
    asyncio.create_task(send())
    print('end_as')


@app.websocket("/stream")
async def stream(ws: WebSocket):
    await ws.accept()

    ws_id = random.randint(0, 1 << 30)
    ws_dict[ws_id] = ws

    print(f"{ws_id} connected")

    try:
        while True:
            data = await ws.receive_json()
    except:
        del ws_dict[ws_id]
        print(f"{ws_id} disconnected")


if __name__ == "__main__":
    start()
    manager = Manager()
    image = manager.Value("image", None)
    results = manager.Value("results", None)
    asyncio.create_task(send())

    # uvicorn.run(app, port=5000, host='0.0.0.0')
    uvicorn.run(app, host="0.0.0.0", port=5000)
