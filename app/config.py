import os
from dotenv import load_dotenv
from ultralytics import YOLO

load_dotenv()

CAMERA_LOGIN = os.environ['CAMERA_LOGIN']
CAMERA_PASSWORD = os.environ['CAMERA_PASSWORD']

URL = f'rtsp://{CAMERA_LOGIN}:{CAMERA_PASSWORD}@192.168.1.108:554/cam/realmonitor?channel=1&subtype=0'

model = YOLO("weights/best.pt")


# @dataclass
# class Config:
#     CAMERA_LOGIN: str
#     CAMERA_PASSWORD: str
#     URL: str
#     model: YOLO
#
#
# def load_config() -> Config:
#     load_dotenv()
#     camera_login = os.environ['CAMERA_LOGIN']
#     camera_password = os.environ['CAMERA_PASSWORD']
#
#     url = f'rtsp://{camera_login}:{camera_password}@192.168.1.108:554/cam/realmonitor?channel=1&subtype=0'
#
#     return Config(camera_login, camera_password, url, YOLO("yolov7/weights/best.pt"))
