import asyncio
import random

import uvicorn
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.requests import Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict
from multiprocessing import Process, Manager

from camera import *
from routers import admin

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
    x = Process(target=camera, args=(image, results))
    x.start()

    asyncio.create_task(send())


@app.websocket("/stream")
async def stream(ws: WebSocket):
    await ws.accept()

    ws_id = random.randint(0, 1 << 30)
    ws_dict[ws_id] = ws

    print(f"{ws_id} connected")

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
    print(db_conn)
    image = manager.Value("image", None)
    results = manager.Value("results", None)

    # uvicorn.run(app, port=5000, host='0.0.0.0')
    uvicorn.run(app, port=5000, host='127.0.0.1')
