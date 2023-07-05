import cv2
import os
from dotenv import load_dotenv

load_dotenv()

CAMERA_LOGIN = os.environ['CAMERA_LOGIN']
CAMERA_PASSWORD = os.environ['CAMERA_PASSWORD']

URL = f'rtsp://{CAMERA_LOGIN}:{CAMERA_PASSWORD}@192.168.1.108:554/cam/realmonitor?channel=1&subtype=0'
