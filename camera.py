import cv2
import os
from dotenv import load_dotenv
from ultralytics import YOLO

load_dotenv()

CAMERA_LOGIN = os.environ['CAMERA_LOGIN']
CAMERA_PASSWORD = os.environ['CAMERA_PASSWORD']

RTSP_URL = f'rtsp://{CAMERA_LOGIN}:{CAMERA_PASSWORD}@192.168.1.108:554/cam/realmonitor?channel=1&subtype=0'

model = YOLO("best.pt")

vid = cv2.VideoCapture(RTSP_URL, cv2.CAP_FFMPEG)

while cv2.waitKey(1) & 0xFF != ord('q'):
    ret, img = vid.read()

    results = model.predict(source=img, conf=0.5, verbose=False)

    img = results[0].orig_img
    classes = results[0].names

    for i in range(len(results[0].boxes.cls)):
        c = classes[int(results[0].boxes.cls[i])]

        cv2.rectangle(
            img,
            list(map(int, results[0].boxes.xyxy[i][:2].tolist())),
            list(map(int, results[0].boxes.xyxy[i][2:].tolist())),
            (0, 0, 255) if "no_" in c else (0, 255, 0),
            4
        )

        xn, yn = map(int, results[0].boxes.xyxy[i][:2].tolist())

        cv2.putText(
            img,
            c,
            (xn, yn),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 255),
            1,
            cv2.LINE_AA
        )

    cv2.imshow('frame', img)
