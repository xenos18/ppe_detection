import asyncio
import random
import threading
import time

import numpy as np
import uvicorn
from fastapi import FastAPI, WebSocket
from fastapi.responses import StreamingResponse, HTMLResponse, Response
from fastapi.requests import Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from typing import Dict
from multiprocessing import Process, Manager, Value

from camera import *

app = FastAPI()

manager: Manager
image: Value
results: Value

ws_dict: Dict[int, WebSocket] = {}

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


async def send():
    while True:
        for ws_id in ws_dict.keys():
            ws = ws_dict[ws_id]
            if image.value is None:
                continue

            await ws.send_bytes(image.value)
            await ws.send_json({
                "type": "detection",
                "ok": True,
                "humans": results.value
            })

        await asyncio.sleep(0.3)


@app.on_event('startup')
async def start():
    pass
    x = Process(target=camera, args=(image, results))
    x.start()

    asyncio.create_task(send())


@app.websocket("/stream")
async def stream(ws: WebSocket):
    await ws.accept()

    ws_id = random.randint(0, 1 << 30)
    ws_dict[ws_id] = ws

    try:
        while True:
            data = await ws.receive_json()
            print(data)
    except:
        del ws_dict[ws_id]
        print(f"{ws_id} disconnected")


@app.get("/", response_class=HTMLResponse)
async def main(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

if __name__ == "__main__":
    manager = Manager()
    image = manager.Value("image", None)
    results = manager.Value("results", None)

    uvicorn.run(app)
