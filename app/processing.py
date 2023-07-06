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


def generate_frames():
    """Получение и обработка потока"""
    capture = cv2.VideoCapture('main.avi', cv2.CAP_FFMPEG)
    while True:
        ret, frame = capture.read()
        if not ret:
            break
        pred, list_of_coords = make_pose_prediction(model, frame)
        hands = Boxlos()
        shoe = ShoesLos()
        # box_list = gg.find(frame, list_of_coords)
        box_list = get_bb(frame, list_of_coords) + hands.find(frame, list_of_coords) + shoe.find(frame, list_of_coords)

        # plot_pose_prediction(frame, pred, show_bbox=True)
        plot_wear_prediction(frame, box_list)

        _, jpeg = cv2.imencode(".jpg", frame)
        frame_bytes = jpeg.tobytes()
        yield (b"--frame\r\n"
               b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n\r\n")
    capture.release()
