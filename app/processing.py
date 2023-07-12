import cv2
import config


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

        _, jpeg = cv2.imencode(".jpg", img)
        frame_bytes = jpeg.tobytes()
        yield (b"--frame\r\n"
               b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n\r\n")
    capture.release()
