import cv2
import config
import sys
from daniil import Boxlos
from danil import get_bb
from shoes import ShoesLos
from yolov7 import *


def plot_wear_prediction(img, boxs):
    for box in boxs:
        print(box)
        if box:
            color = (0, 255, 0) if box[4] else (0, 0, 255)
            cv2.rectangle(img, (box[0], box[1]), (box[2], box[3]), color, 3)
            print(True)


def prediction(frame):
    results = config.model.predict(source=frame, conf=0.5, verbose=False)

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

    return img


def generate_frames():
    """Получение и обработка потока"""
    capture = cv2.VideoCapture(config.URL, cv2.CAP_FFMPEG)
    while True:
        ret, frame = capture.read()
        if not ret:
            break

        img = prediction(frame)


        # pred, list_of_coords = make_pose_prediction(model, frame)
        # hands = Boxlos()
        # shoe = ShoesLos()
        # # box_list = gg.find(frame, list_of_coords)
        # box_list = get_bb(frame, list_of_coords) + hands.find(frame, list_of_coords) + shoe.find(frame, list_of_coords)
        #
        # # plot_pose_prediction(frame, pred, show_bbox=True)
        # plot_wear_prediction(frame, box_list)

        _, jpeg = cv2.imencode(".jpg", img)
        frame_bytes = jpeg.tobytes()
        yield (b"--frame\r\n"
               b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n\r\n")
    capture.release()
