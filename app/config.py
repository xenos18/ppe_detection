import os
from dotenv import load_dotenv
from ultralytics import YOLO
load_dotenv()

CAMERA_LOGIN = os.environ['CAMERA_LOGIN']
CAMERA_PASSWORD = os.environ['CAMERA_PASSWORD']

model = YOLO("weights/best.pt", task="detect")
pose = YOLO("weights/yolov8m-pose.pt")


DRAW_HUMAN_BBOX = False
DRAW_SIZ_BBOX = True
DRAW_SINGLE_HUMAN_BBOX = False

RTSP_URL = f'rtsp://{CAMERA_LOGIN}:{CAMERA_PASSWORD}@192.168.1.108:554/cam/realmonitor?channel=1&subtype=0'

bx = {
    "hood": [0, 1, 2, 3, 4],
    "glasses": [1, 2],
    "mask": [0],
    "suit": [5, 6, 11, 12, 13, 14],
    "glove": [9, 10],
    "shoe": [15, 16]
}


# @dataclass
# class Config:
#     CAMERA_LOGIN: str
#     CAMERA_PASSWORD: str
#     URL: str
#     model: YOLO

#
# def load_config() -> Config:
#     load_dotenv()
#     camera_login = os.environ['CAMERA_LOGIN']
#     camera_password = os.environ['CAMERA_PASSWORD']
#
#     url = f'rtsp://{camera_login}:{camera_password}@192.168.1.108:554/cam/realmonitor?channel=1&subtype=0'
#
#     return Config(camera_login, camera_password, url, YOLO("yolov7/weights/best.pt"))
