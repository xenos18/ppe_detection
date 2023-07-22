
from multiprocessing import Value

import numpy as np
from shapely.geometry import *
from video.VideoCapture import *
from config import *
import json
from video.sequence import Sequence
from datetime import datetime
import base64


items = bx.keys()
double = ["glove", "shoe"]

DIST_THRESHOLD = 100

last = dict()
with open('sequence/seq.json') as file:
    seq = json.load(file)["sequence"]
seq = Sequence(seq)

frameID = 0


def camera(image: Value, results: Value):
    global frameID

    vid = VideoCapture(1)
    print('Camera Working')

    while True:
        frameID += 1
        frame = vid.read()

        if frame is None:
            continue

        box_results = model.predict(source=frame, conf=MODEL_CONF, verbose=False)
        pose_results = pose.track(source=frame, conf=0.4, persist=True, verbose=False)

        img = box_results[0].orig_img
        classes = box_results[0].names

        detected_cls = list(map(lambda x: classes[int(x)], box_results[0].boxes.cls))  # convert classes ids to names

        humans = []

        for i in range(len(pose_results[0].keypoints)):  # some transforms
            humans.append([[0, 0] for _ in range(len(pose_results[0].keypoints.xy[i]))])
            for j in range(len(pose_results[0].keypoints.xy[i])):
                humans[i][j] = pose_results[0].keypoints.xy[i][j]

        in_results = [{
            "items": dict(zip(items, [[], [], [], [], [], []])),
            "correct": {}
        } for i in range(len(pose_results[0].boxes.xyxy))]

        for i in range(len(box_results[0].boxes.cls)):  # finding box for every body part
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
                    d = p.distance(Point(humans[j][k].to("cpu")))

                    if d < min_dist and d < DIST_THRESHOLD:
                        min_dist = d
                        min_v = j
            if min_v >= 0:
                in_results[min_v]["items"][c.replace("no_", "")].append(i)

        for i in range(len(in_results)):
            x0, y0, x1, y1 = map(int, pose_results[0].boxes.xyxy[i])
            track_id = int(pose_results[0].boxes[i].id) if pose_results[0].boxes[i].id is not None else 0

            if track_id not in last.keys():  # predict normalization with geometric progression coefficients b[i] = FUNC_B * FUNC_Q ** i
                last[track_id] = dict()
                for k in items:
                    if k not in double:
                        last[track_id][k] = 0
                    else:
                        last[track_id][f"left_{k}"] = 0
                        last[track_id][f"right_{k}"] = 0
                last[track_id]["max"] = 0

            for k in bx.keys():
                if k not in double:
                    last[track_id][k] *= FUNC_Q
                else:
                    last[track_id][f"left_{k}"] *= FUNC_Q
                    last[track_id][f"right_{k}"] *= FUNC_Q
            last[track_id]["max"] = FUNC_Q * last[track_id]["max"] + FUNC_B

            if DRAW_HUMAN_BBOX:
                cv2.rectangle(img, (x0, y0), (x1, y1), (255, 0, 0), 4)
                cv2.putText(img, str(int(pose_results[0].boxes[i].id)) if pose_results[0].boxes[i].id is not None else "no_track", (x0, y0), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 1, cv2.LINE_AA)

            for k in bx:  # add data to WebSocket response
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
                mv = [""] if k not in double else ["left_", "right_"]
                for q in range(len(mv)):  # normalize
                    pref = mv[q]
                    last[track_id][pref + k] += in_results[i]["correct"][pref + k] * FUNC_B

                    in_results[i]["correct"][pref + k] = last[track_id][pref + k] / last[track_id]["max"] > 0.5
                    if q < len(in_results[i]["items"][k]):  # draw box
                        x0, y0, x1, y1 = map(int, box_results[0].boxes.xyxy[in_results[i]["items"][k][q]])

                        if DRAW_SIZ_BBOX:
                            cv2.rectangle(img, (x0, y0), (x1, y1),
                                          (0, 255, 0) if in_results[i]["correct"][pref + k] else (0, 0, 255), 4)
                            cv2.putText(img, f"{pref + k} (id = {track_id})", (x0, y0), cv2.FONT_HERSHEY_SIMPLEX, 1,
                                        (255, 255, 255), 1, cv2.LINE_AA)

        mx_v = 0
        mx_a = 0
        for i in range(len(in_results)):
            _, _, w, h = pose_results[0].boxes.xywh[i]
            if w * h > mx_a:
                mx_a = w * h
                mx_v = i

        # if seq.frame_count == 0:
        #     seq.id_now = mx_v
        #     seq.time_in = datetime.now()
        #     seq.prediction(box_results)
        # else:
        #     if seq.id_now != mx_v:
        #         seq.time_out = datetime.now()
        #         seq.add_event()
        #         seq.id_now = mx_v
        #         seq.create_check_dict()
        #         seq.prediction(box_results)
        #     else:
        #         seq.prediction(box_results)

        if mx_a > 0:  # highlight biggest-area human
            x0, y0, x1, y1 = map(int, pose_results[0].boxes.xyxy[mx_v])
            tmp = img[y0:y1, x0:x1].copy()
            img = (img.astype(np.float64) / 2 + 127.5).astype(np.uint8)
            img[y0:y1, x0:x1] = tmp

            if not DRAW_HUMAN_BBOX and DRAW_SINGLE_HUMAN_BBOX:
                cv2.rectangle(
                    img,
                    (x0, y0),
                    (x1, y1),
                    (255, 0, 0),
                    4
                )
        else:
            img = (img.astype(np.float64) / 2 + 127.5).astype(np.uint8)

        image.value = cv2.imencode('.jpg', img)[1].tobytes()

        results.value = list(map(lambda x: x["correct"], in_results))[mx_v:mx_v+1]
