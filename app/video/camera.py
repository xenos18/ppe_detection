
from multiprocessing import Value
from shapely.geometry import *
from .VideoCapture import *
from config import *


items = bx.keys()
double = ["glove", "shoe"]


def camera(image: Value, results: Value):
    vid = VideoCapture(RTSP_URL)
    while True:
        frame = vid.read()

        if frame is None:
            continue

        box_results = model.predict(source=frame, conf=0.5, verbose=False)
        pose_results = pose.track(source=frame, conf=0.4, persist=True, verbose=False)

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
                    d = p.distance(Point(humans[j][k].to("cpu")))

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

            if DRAW_HUMAN_BBOX:
                cv2.rectangle(
                    img,
                    (x0, y0),
                    (x1, y1),
                    (255, 0, 0),
                    4
                )

                cv2.putText(
                    img,
                    str(int(pose_results[0].boxes[i].id)),
                    (x0, y0),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (255, 255, 255),
                    1,
                    cv2.LINE_AA
                )

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

        image.value = cv2.imencode('.jpg', img)[1].tobytes()
        results.value = list(map(lambda x: x["correct"], in_results))
