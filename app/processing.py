import cv2
import ffmpeg
import numpy as np
import config


def prediction(frame):

    results = config.model.predict(source=cv2.resize(frame, ( 1280, 720), interpolation = cv2.INTER_AREA), conf=0.5, verbose=False)


    classes = results[0].names

    boxs = results[0].boxes
    for i in range(len(boxs.cls)):
        c = classes[int(boxs.cls[i])]

        up = boxs.xyxy[i][:2].tolist()
        down = boxs.xyxy[i][2:].tolist()

        cv2.rectangle(
            frame,
            (int(up[0]), int(up[1] )),
            (int(down[0]), int(down[1])),
            (0, 0, 255) if "no_" in c else (0, 255, 0),
            4
        )

     

        cv2.putText(
            frame,
            c,
            (int(up[0]), int(up[1] )),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 255),
            1,
            cv2.LINE_AA
        )

    return frame


def generate_frames():
    """Получение и обработка потока"""
    capture = cv2.VideoCapture(config.URL, cv2.CAP_FFMPEG)
    while True:
        ret, frame = capture.read()
        if not ret:
            break

        # img = prediction(frame)

        _, jpeg = cv2.imencode(".jpg", frame)
        frame_bytes = jpeg.tobytes()
        yield (b"--frame\r\n"
               b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n\r\n")
    capture.release()


def read_frames(source):

    args = {"rtsp_transport": "tcp",
    "fflags": "nobuffer",
    "flags": "low_delay"
    }

    probe = ffmpeg.probe(source)
    cap_info = next(x for x in probe['streams'] if x['codec_type'] == 'video')
    width = cap_info['width'] 
    height = cap_info['height']

    process1 = (
   
    )

    while True:
        in_bytes = process1.stdout.read(width * height * 3)
        if not in_bytes:
            break

        in_frame = (
            np
            .frombuffer(in_bytes, np.uint8)
            .reshape([height, width, 3])
            )

        frame = cv2.cvtColor(in_frame, cv2.COLOR_RGB2BGR)

        img = prediction(frame)

        _, jpeg = cv2.imencode(".jpg", img)
        frame_bytes = jpeg.tobytes()
        yield (b"--frame\r\n"
               b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n\r\n")


    process1.kill()