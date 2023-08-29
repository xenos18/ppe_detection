import os
from dotenv import load_dotenv
from ultralytics import YOLO
load_dotenv()

"""RTSP поток"""
# CAMERA_LOGIN = os.environ['CAMERA_LOGIN']
# CAMERA_PASSWORD = os.environ['CAMERA_PASSWORD']
# RTSP_URL = f'rtsp://{CAMERA_LOGIN}:{CAMERA_PASSWORD}@192.168.1.108:554/cam/realmonitor?channel=1&subtype=0'


#
# DRAW_HUMAN_BBOX = False
# DRAW_SIZ_BBOX = True
# DRAW_SINGLE_HUMAN_BBOX = False
# MODEL_CONF = 0.5

FUNC_B = 0.2
FUNC_Q = 1 - FUNC_B


bx = {
    "hood": [0, 1, 2, 3, 4],
    "glasses": [1, 2],
    "mask": [0],
    "suit": [5, 6, 11, 12, 13, 14],
    "left_glove": [9],
    "right_glove": [10],
    "left_shoe": [15],
    "right_shoe": [16]
}

bx_ref = {
    "hood": ["hood"],
    "glasses": ["glasses"],
    "mask": ["mask"],
    "suit": ["suit"],
    "glove": ["left_glove", "right_glove"],
    "shoe": ["left_shoe", "right_shoe"]
}


MAX_BOX_DURATION = 0.5
