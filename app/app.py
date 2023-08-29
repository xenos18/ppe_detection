from typing import Tuple
import numpy as np
from shapely.geometry import *
from config import *
import json
import time
import cv2
import numpy


class DetectingMonitor:

    def __init__(self) -> None:
        """
        Initializes the model.
        """
        self.model = YOLO("video/weights/best.pt", task="detect")
        self.pose = YOLO("video/weights/yolov8s-pose.pt")
        self.ckpt = None  # if loaded from *.pt
        self.cfg = None  # if loaded from *.yaml
        self.ckpt_path = None
        self.overrides = {'human_box': False, 'siz_box': True,
                          'single_human_box': False}  # overrides for trainer object
        self.metrics = None  # validation/training metrics
        self.session = None  # HUB session
        self.items = bx.keys()

        self.DIST_THRESHOLD = 100

        self.last = dict()

        self.track_elements = {}

    def get_sequence(self):
        with open('sequence/seq.json') as file:
            seq = json.load(file)["sequence"]
        return seq

    def prediction(self, source=None, stream=False, predictor=None, **kwargs):
        """
        Perform prediction using the YOLO model.

        Args:
            source (str | int | PIL | np.ndarray): The source of the image to make predictions on.
                          Accepts all source types accepted by the YOLO model.
            stream (bool): Whether to stream the predictions or not. Defaults to False.
            predictor (BasePredictor): Customized predictor.
            **kwargs : Additional keyword arguments passed to the predictor.
                       Check the 'configuration' section in the documentation for all available options.

        Returns:
            (List[ultralytics.engine.results.Results]): The prediction results.
        """
        if source is None:
            # source = ASSETS
            # LOGGER.warning(f"WARNING ⚠️ 'source' is missing. Using 'source={source}'.")
            print('source None')
            return
        # Check prompts for SAM/FastSAM
        prompts = kwargs.pop('prompts', None)
        overrides = self.overrides.copy()
        overrides['conf'] = 0.4
        overrides.update(kwargs)  # prefer kwargs
        overrides['mode'] = kwargs.get('mode', 'predict')
        frame = self.to_type(source)
        return self.camera(frame, overrides)

    def to_type(self, source):
        if type(source) is str:
            frame = cv2.imread(source)
        elif type(source) is numpy.ndarray:
            return source
        return frame

    def camera(self, frame: numpy.ndarray, args) -> Tuple[numpy.ndarray, list]:
        box_results = self.model.predict(source=frame, conf=args['conf'], verbose=False)

        pose_results = self.pose.track(source=frame, conf=args['conf'], persist=True, verbose=False)

        img = box_results[0].orig_img
        classes = box_results[0].names

        detected_cls = list(map(lambda x: classes[int(x)], box_results[0].boxes.cls))  # convert classes ids to names

        humans = []

        for i in range(len(pose_results[0].keypoints)):  # some transforms
            humans.append([[0, 0] for _ in range(len(pose_results[0].keypoints.xy[i]))])
            for j in range(len(pose_results[0].keypoints.xy[i])):
                humans[i][j] = pose_results[0].keypoints.xy[i][j]

        in_results = [{
            "items": dict(zip(self.items, [[] for _ in self.items])),
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

                        if d < min_dist and d < self.DIST_THRESHOLD:
                            min_dist = d
                            min_v = j
                            chosen_name = checking_name
            if min_v >= 0:
                in_results[min_v]["items"][chosen_name].append(i)

        for i in range(len(in_results)):
            x0, y0, x1, y1 = map(int, pose_results[0].boxes.xyxy[i])
            track_id = int(pose_results[0].boxes[i].id) if pose_results[0].boxes[i].id is not None else 0

            if track_id not in self.last.keys():  # predict normalization with
                # geometric progression coefficients b[i] = FUNC_B * FUNC_Q ** i
                self.last[track_id] = dict()
                self.track_elements[track_id] = dict()
                for k in self.items:
                    self.last[track_id][k] = 0
                    self.track_elements[track_id][k] = {
                        "time": 0,
                        "box": (0, 0, 0, 0),
                        "correct": False
                    }

                self.last[track_id]["max"] = 0

            for k in bx.keys():
                self.last[track_id][k] *= FUNC_Q

            self.last[track_id]["max"] = FUNC_Q * self.last[track_id]["max"] + FUNC_B

            if args['human_box']:
                cv2.rectangle(img, (x0, y0), (x1, y1), (255, 0, 0), 4)
                cv2.putText(img, str(int(pose_results[0].boxes[i].id)) if pose_results[0].boxes[
                                                                              i].id is not None else "no_track",
                            (x0, y0), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 1, cv2.LINE_AA)

            for k in bx:  # add data to WebSocket response
                in_results[i]["items"][k].sort(key=lambda x: box_results[0].boxes.xywh[x][0])

                in_results[i]["items"][k] = in_results[i]["items"][k][:1]
                in_results[i]["correct"][k] = len(in_results[i]["items"][k]) > 0 and "no_" not in detected_cls[
                    in_results[i]["items"][k][0]]

                self.last[track_id][k] += in_results[i]["correct"][k] * FUNC_B

                in_results[i]["correct"][k] = self.last[track_id][k] / self.last[track_id]["max"] > 0.5
                x0, y0, x1, y1, correct = None, None, None, None, None
                if len(in_results[i]["items"][k]) == 0 and time.time() - self.track_elements[track_id][k][
                    "time"] < MAX_BOX_DURATION:
                    x0, y0, x1, y1 = self.track_elements[track_id][k]["box"]
                    in_results[i]["correct"][k] = correct = self.track_elements[track_id][k]["correct"]
                elif len(in_results[i]["items"][k]) > 0:
                    x0, y0, x1, y1 = map(int, box_results[0].boxes.xyxy[in_results[i]["items"][k][0]])
                    correct = in_results[i]["correct"][k]

                    self.track_elements[track_id][k] = {
                        "time": time.time(),
                        "box": (x0, y0, x1, y1),
                        "correct": correct
                    }

                if correct is not None and args['siz_box']:
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

        # if seq.frame_count == 0:
        #     seq.id_now = mx_v
        #     seq.time_in = datetime.now()
        #     seq.prediction(box_results)
        # else:
        #     if seq.id_now != mx_v:
        #         seq.time_out = datetime.now()
        #         print('Вызов ....')
        #         seq.add_event(edited)
        #         seq.id_now = mx_v
        #         seq.create_check_dict()
        #         seq.prediction(box_results)
        #     else:
        #         seq.prediction(box_results)

        if mx_a > 0:  # highlight biggest-area human
            x0, y0, x1, y1 = map(int, pose_results[0].boxes.xyxy[mx_v])
            h, w, _ = frame.shape
            x0, y0, x1, y1 = max(0, x0), max(0, y0), min(w - 1, x1), min(h - 1, y1)
            tmp = img[y0:y1, x0:x1].copy()
            img = (img.astype(np.float64) / 2 + 127.5).astype(np.uint8)
            img[y0:y1, x0:x1] = tmp

            if not args['human_box'] and args['single_human_box']:
                cv2.rectangle(
                    img,
                    (x0, y0),
                    (x1, y1),
                    (255, 0, 0),
                    4
                )
        else:
            img = (img.astype(np.float64) / 2 + 127.5).astype(np.uint8)

        return frame, list(map(lambda x: x["correct"], in_results))[mx_v:mx_v + 1]


if __name__ == '__main__':
    mod = DetectingMonitor()
    new_frame, odj = mod.prediction('img.png', box=True, conf=0.5)
    print(odj)
    print(type(new_frame), type(odj))
    cv2.imshow("Image", new_frame)
    cv2.waitKey(0)
