from database import run
import asyncio
import random

import uvicorn
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict
from multiprocessing import Process, Manager
from sqlalchemy.orm import sessionmaker
from database import _init
from video import Value, camera
from routers import admin
from bot import start_bot
from crud import get_events_sh_last

run()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_init())
image: Value
results: Value
edited: Value
form: Value
ws_dict: Dict[int, WebSocket] = {}


async def send():
    while True:
        for ws_id in ws_dict.keys():
            ws = ws_dict[ws_id]
            if image.value is None:
                continue

            data = {
                "type": "detection",
                "ok": True,
                "humans": results.value,
            }
            if edited.value:
                with SessionLocal() as sess:
                    error = [i.serialize() for i in get_events_sh_last(sess)]
                data['edited'] = error
                edited.value = False
            print(form.value)
            if form.value:
                data['form'] = form.value
                form.value = ''

            try:
                await ws.send_bytes(image.value)
                await ws.send_json(data)
            except Exception as e:
                print(f"Ooops! {e}")

        await asyncio.sleep(0.1)


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


@app.on_event('startup')
async def start():
    Process(target=camera, args=(image, results, edited, form)).start()
    # Process(target=start_bot, args=(image,)).start()

    asyncio.create_task(send())


@app.websocket("/stream")
async def stream(ws: WebSocket):
    print("aa")
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


if __name__ == "__main__":
    manager = Manager()
    image = manager.Value("image", None)
    results = manager.Value("results", None)
    edited = manager.Value("edited", True)
    form = manager.Value("form", "Работаем")

    uvicorn.run(app, port=8500, host='0.0.0.0')
