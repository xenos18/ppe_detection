import random
import threading
from multiprocessing import Value
import cv2
from ultralytics import YOLO
from shapely.geometry import *
from dotenv import load_dotenv
import os
from VideoCapture import *
from database.connect import *
from queue import Queue
from deepface import DeepFace
import pandas as pd

load_dotenv()

DRAW_HUMAN_BBOX = True
DRAW_SIZ_BBOX = True

CAMERA_LOGIN = os.environ['CAMERA_LOGIN']
CAMERA_PASSWORD = os.environ['CAMERA_PASSWORD']
RTSP_URL = f'rtsp://{CAMERA_LOGIN}:{CAMERA_PASSWORD}@192.168.1.108:554/cam/realmonitor?channel=1&subtype=0'

model = YOLO("best.pt", task="detect")
pose = YOLO("yolov8m-pose.pt")

bx = {
    "hood": [0, 1, 2, 3, 4],
    "glasses": [1, 2],
    "mask": [0],
    "suit": [5, 6, 11, 12, 13, 14],
    "glove": [9, 10],
    "shoe": [15, 16]
}

items = bx.keys()
double = ["glove", "shoe"]


tracks = dict()
track_queue = Queue()

session = Session(engine)

users = list(session.scalars(select(User)))
user_ids = list(map(lambda x: x.id, users))

cnt_v = 0
def process_queue():
    global cnt_v

    while True:
        if track_queue.empty():
            continue

        track_id, img = track_queue.get()
        res = DeepFace.find(img, "faces/compiled", enforce_detection=False)[0]

        u_ids = set(user_ids)
        for i in range(len(res)):
            name = res.at[i, "identity"]
            val = float(res.at[i, "VGG-Face_cosine"])

            user_id = int(name.replace(".jpg", "").replace("faces/compiled/", ""), 16) >> 128
            if user_id in u_ids:
                u_ids.remove(user_id)
                tracks[track_id][user_id] += val

        for u_id in u_ids:
            tracks[track_id][u_id] += 1

        # cnt_v += 1
        # path = f"debug/{cnt_v}"
        # if not os.path.exists(path):
        #     os.mkdir(path)
        #
        # cv2.imwrite(f"{path}/img.jpg", img)
        # res.to_csv(f"{path}/table.csv")


p_th = threading.Thread(target=process_queue, daemon=True)
p_th.start()


def camera(image: Value, results: Value):
    vid = VideoCapture(RTSP_URL)
    while True:
        frame = vid.read()

        if frame is None:
            continue

        box_results = model.predict(source=frame, conf=0.5, verbose=False)
        pose_results = pose.track(source=frame, conf=0.4, persist=True, verbose=False, tracker="bytetrack.yaml")

        img = box_results[0].orig_img.copy()
        classes = box_results[0].names

        detected_cls = list(map(lambda x: classes[int(x)], box_results[0].boxes.cls))

        humans = []

        for i in range(len(pose_results[0].keypoints)):
            humans.append([[0, 0] for _ in range(len(pose_results[0].keypoints.xy[i]))])
            for j in range(len(pose_results[0].keypoints.xy[i])):
                humans[i][j] = pose_results[0].keypoints.xy[i][j]

        in_results = [{
            "items": dict(zip(items, [[], [], [], [], [], []])),
            "correct": {}
        } for i in range(len(pose_results[0].boxes.xyxy))]

        for i in range(len(box_results[0].boxes.cls)):
            c = detected_cls[i]
            x0, y0, x1, y1 = map(int, box_results[0].boxes.xyxy[i])

            min_dist = float("inf")
            min_v = -1

            p = Polygon(
                [[x0, y0], [x1, y0], [x1, y1], [x0, y1]])
            for j in range(len(humans)):
                for k in bx[c.replace("no_", "")]:
                    if k >= len(humans[j]):
                        continue
                    d = p.distance(Point(humans[j][k]))

                    if d < min_dist:
                        min_dist = d
                        min_v = j
            if min_v >= 0:
                in_results[min_v]["items"][c.replace("no_", "")].append(i)

                track_id = int(pose_results[0].boxes[min_v].id)

                if DRAW_SIZ_BBOX:
                    cv2.rectangle(
                        img,
                        (x0, y0),
                        (x1, y1),
                        (0, 0, 255) if "no_" in c else (0, 255, 0),
                        4
                    )

                    cv2.putText(
                        img,
                        f"{c} (id = {track_id})",
                        (x0, y0),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (255, 255, 255),
                        1,
                        cv2.LINE_AA
                    )

        for i in range(len(in_results)):
            x0, y0, x1, y1 = map(int, pose_results[0].boxes.xyxy[i])

            if len(in_results[i]["items"]["hood"]) > 0 and pose_results[0].boxes[i].id is not None:
                track_id = int(pose_results[0].boxes[i].id)
                if track_id not in tracks.keys():
                    tracks[track_id] = {}
                    for u_id in user_ids:
                        tracks[track_id][u_id] = 0

                if random.random() < 0.3:
                    ind = in_results[i]["items"]["hood"][0]
                    x0, y0, x1, y1 = map(int, box_results[0].boxes.xyxy[ind])
                    track_queue.put([track_id, frame[y0:y1, x0:x1]])

            for k in bx:
                in_results[i]["items"][k].sort(key=lambda x: box_results[0].boxes.xywh[x][0])
                if k not in double:
                    in_results[i]["items"][k] = in_results[i]["items"][k][:1]
                    in_results[i]["correct"][k] = len(in_results[i]["items"][k]) > 0 and "no_" not in detected_cls[
                        in_results[i]["items"][k][0]]
                else:
                    if len(in_results[i]["items"][k]) > 2:
                        in_results[i]["items"][k] = [in_results[i]["items"][k][0], in_results[i]["items"][k][-1]]

                    in_results[i]["correct"][f"left_{k}"] = len(in_results[i]["items"][k]) > 0 and "no_" not in \
                                                            detected_cls[in_results[i]["items"][k][0]]
                    in_results[i]["correct"][f"right_{k}"] = len(in_results[i]["items"][k]) > 1 and "no_" not in \
                                                             detected_cls[in_results[i]["items"][k][1]]

            if DRAW_HUMAN_BBOX:
                cv2.rectangle(
                    img,
                    (x0, y0),
                    (x1, y1),
                    (255, 0, 0),
                    4
                )

                if pose_results[0].boxes[i].id is not None and int(pose_results[0].boxes[i].id) in tracks.keys():
                    track_id = int(pose_results[0].boxes[i].id)
                    mx_v = user_ids[0]
                    for user_id in user_ids:
                        if tracks[track_id][user_id] < tracks[track_id][mx_v]:
                            mx_v = user_id

                    cv2.putText(
                        img,
                        str(mx_v),
                        (x0, y0),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (255, 255, 255),
                        1,
                        cv2.LINE_AA
                    )

        image.value = cv2.imencode('.jpg', img)[1].tobytes()
        results.value = list(map(lambda x: x["correct"], in_results))
