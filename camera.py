from multiprocessing import Value
import cv2
from ultralytics import YOLO
from shapely.geometry import *
from dotenv import load_dotenv
import os

load_dotenv()

CAMERA_LOGIN = os.environ['CAMERA_LOGIN']
CAMERA_PASSWORD = os.environ['CAMERA_PASSWORD']
RTSP_URL = f'rtsp://{CAMERA_LOGIN}:{CAMERA_PASSWORD}@192.168.1.108:554/cam/realmonitor?channel=1&subtype=0'


model = YOLO("best.pt", task="detect")
pose = YOLO("yolov8n-pose.pt")

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


def camera(image: Value, results: Value):
    vid = cv2.VideoCapture(RTSP_URL)

    while True:
        ret, img = vid.read()

        box_results = model.predict(source=img, conf=0.5, verbose=False)
        pose_results = pose.predict(source=img, conf=0.5, verbose=False)

        img = box_results[0].orig_img
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
        } for i in range(len(pose_results[0].keypoints))]

        for i in range(len(box_results[0].boxes.cls)):
            c = classes[int(box_results[0].boxes.cls[i])]
            coords = box_results[0].boxes.xyxy[i]

            min_dist = float("inf")
            min_v = -1

            p = Polygon([[coords[0], coords[1]], [coords[2], coords[1]], [coords[2], coords[3]], [coords[0], coords[3]]])
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

            cv2.rectangle(
                img,
                list(map(int, coords[:2].tolist())),
                list(map(int, coords[2:].tolist())),
                (0, 0, 255) if "no_" in c else (0, 255, 0),
                4
            )

            xn, yn = map(int, box_results[0].boxes.xyxy[i][:2].tolist())

            cv2.putText(
                img,
                f"{c} (id = {min_v})",
                (xn, yn),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (255, 255, 255),
                1,
                cv2.LINE_AA
            )

        for i in range(len(in_results)):
            for k in bx:
                in_results[i]["items"][k].sort(key=lambda x: box_results[0].boxes.xywh[x][0])
                if k not in double:
                    in_results[i]["items"][k] = in_results[i]["items"][k][:1]
                    in_results[i]["correct"][k] = len(in_results[i]["items"][k]) > 0 and "no_" not in detected_cls[in_results[i]["items"][k][0]]
                else:
                    if len(in_results[i]["items"][k]) > 2:
                        in_results[i]["items"][k] = [in_results[i]["items"][k][0], in_results[i]["items"][k][-1]]

                    in_results[i]["correct"][f"left_{k}"] = len(in_results[i]["items"][k]) > 0 and "no_" not in detected_cls[in_results[i]["items"][k][0]]
                    in_results[i]["correct"][f"right_{k}"] = len(in_results[i]["items"][k]) > 1 and "no_" not in detected_cls[in_results[i]["items"][k][1]]

        image.value = cv2.imencode('.jpg', img)[1].tobytes()
        results.value = list(map(lambda x: x["correct"], in_results))
