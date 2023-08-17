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

DIST_THRESHOLD = 100

last = dict()


def get_seq():
    with open('sequence/seq.json') as file:
        seq = json.load(file)["sequence"]
    return seq


frameID = 0
track_elements = {}


def camera(image: Value, results: Value, edited: Value, form: Value):
    global frameID
    seq = Sequence(get_seq(), form)
    vid = VideoCapture(0)
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
            "items": dict(zip(items, [[] for _ in items])),
            "correct": {}
        } for i in range(len(pose_results[0].boxes.xyxy))]

        for i in range(len(box_results[0].boxes.cls)):  # finding box for every body part
            c = detected_cls[i]
            x0, y0, x1, y1 = map(int, box_results[0].boxes.xyxy[i])

            min_dist = float("inf")
            min_v = -1
            orig_name = c.replace("no_", "")
            chosen_name = ""

            p = Polygon(
                [[x0, y0], [x1, y0], [x1, y1], [x0, y1]])
            for j in range(len(humans)):
                for checking_name in bx_ref[orig_name]:
                    for k in bx[checking_name]:
                        if k >= len(humans[j]):
                            continue
                        d = p.distance(Point(humans[j][k].to("cpu")))

                        if d < min_dist and d < DIST_THRESHOLD:
                            min_dist = d
                            min_v = j
                            chosen_name = checking_name
            if min_v >= 0:
                in_results[min_v]["items"][chosen_name].append(i)

        for i in range(len(in_results)):
            x0, y0, x1, y1 = map(int, pose_results[0].boxes.xyxy[i])
            track_id = int(pose_results[0].boxes[i].id) if pose_results[0].boxes[i].id is not None else 0

            if track_id not in last.keys():  # predict normalization with
                # geometric progression coefficients b[i] = FUNC_B * FUNC_Q ** i
                last[track_id] = dict()
                track_elements[track_id] = dict()
                for k in items:
                    last[track_id][k] = 0
                    track_elements[track_id][k] = {
                        "time": 0,
                        "box": (0, 0, 0, 0),
                        "correct": False
                    }

                last[track_id]["max"] = 0

            for k in bx.keys():
                last[track_id][k] *= FUNC_Q

            last[track_id]["max"] = FUNC_Q * last[track_id]["max"] + FUNC_B

            if DRAW_HUMAN_BBOX:
                cv2.rectangle(img, (x0, y0), (x1, y1), (255, 0, 0), 4)
                cv2.putText(img, str(int(pose_results[0].boxes[i].id)) if pose_results[0].boxes[
                                                                              i].id is not None else "no_track",
                            (x0, y0), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 1, cv2.LINE_AA)

            for k in bx:  # add data to WebSocket response
                in_results[i]["items"][k].sort(key=lambda x: box_results[0].boxes.xywh[x][0])

                in_results[i]["items"][k] = in_results[i]["items"][k][:1]
                in_results[i]["correct"][k] = len(in_results[i]["items"][k]) > 0 and "no_" not in detected_cls[
                    in_results[i]["items"][k][0]]

                last[track_id][k] += in_results[i]["correct"][k] * FUNC_B

                in_results[i]["correct"][k] = last[track_id][k] / last[track_id]["max"] > 0.5
                x0, y0, x1, y1, correct = None, None, None, None, None
                if len(in_results[i]["items"][k]) == 0 and time.time() - track_elements[track_id][k][
                    "time"] < MAX_BOX_DURATION:
                    x0, y0, x1, y1 = track_elements[track_id][k]["box"]
                    in_results[i]["correct"][k] = correct = track_elements[track_id][k]["correct"]
                elif len(in_results[i]["items"][k]) > 0:
                    x0, y0, x1, y1 = map(int, box_results[0].boxes.xyxy[in_results[i]["items"][k][0]])
                    correct = in_results[i]["correct"][k]

                    track_elements[track_id][k] = {
                        "time": time.time(),
                        "box": (x0, y0, x1, y1),
                        "correct": correct
                    }

                if correct is not None and DRAW_SIZ_BBOX:
                    cv2.rectangle(img, (x0, y0), (x1, y1), (0, 255, 0) if correct else (0, 0, 255), 4)
                    cv2.putText(img, f"{k} (id = {track_id})", (x0, y0), cv2.FONT_HERSHEY_SIMPLEX, 1,
                                (255, 255, 255), 1, cv2.LINE_AA)

        mx_v = 0
        mx_a = 0
        for i in range(len(in_results)):
            _, _, w, h = pose_results[0].boxes.xywh[i]
            if w * h > mx_a:
                mx_a = w * h
                mx_v = i

        if seq.frame_count == 0:
            seq.id_now = mx_v
            seq.time_in = datetime.now()
            seq.prediction(box_results)
        else:
            if seq.id_now != mx_v:
                seq.time_out = datetime.now()
                print('Вызов ....')
                seq.add_event(edited)
                seq.id_now = mx_v
                seq.create_check_dict()
                seq.prediction(box_results)
            else:
                seq.prediction(box_results)

        if mx_a > 0:  # highlight biggest-area human
            x0, y0, x1, y1 = map(int, pose_results[0].boxes.xyxy[mx_v])
            h, w, _ = frame.shape
            x0, y0, x1, y1 = max(0, x0), max(0, y0), min(w - 1, x1), min(h - 1, y1)
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

        image.value = cv2.imencode('.jpg', frame)[1].tobytes()

        results.value = list(map(lambda x: x["correct"], in_results))[mx_v:mx_v + 1]
