import cv2
import ffmpeg
import numpy as np
import config


def prediction(frame):
    image = cv2.resize(frame, (640, 640))
    results = config.model.predict(source=image, conf=0.5, verbose=False)

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
    capture = cv2.VideoCapture(0, cv2.CAP_FFMPEG)
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
        ffmpeg
        .input(source, **args)
        .output('pipe:', format='rawvideo', pix_fmt='rgb24')
        .overwrite_output()
        .run_async(pipe_stdout=True)
    )

    while True:
        in_bytes = process1.stdout.read(width * height * 3)
        if not in_bytes:
            break

        in_frame = np.frombuffer(in_bytes, np.uint8).reshape([height, width, 3])

        frame = cv2.cvtColor(in_frame, cv2.COLOR_RGB2BGR)

        img = prediction(frame)

        _, jpeg = cv2.imencode(".jpg", frame)
        frame_bytes = jpeg.tobytes()
        yield (b"--frame\r\n"
               b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n\r\n")

    process1.kill()
