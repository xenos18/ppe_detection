import cv2
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import main
app = FastAPI()


def generate_frames():
    url = f'https://camera.lipetsk.ru//ms-42.camera.lipetsk.ru/live/3bb1eaec-eb20-403d-9a09-5bc92a16da86/playlist.m3u8'
    capture = cv2.VideoCapture(main.URL)
    while True:
        ret, frame = capture.read()
        if not ret:
            break
        # Обработайте кадр, если это необходимо
        # Например, преобразуйте его в формат JPEG для передачи через HTTP
        _, jpeg = cv2.imencode(".jpg", frame)
        frame_bytes = jpeg.tobytes()
        yield (b"--frame\r\n"
               b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n\r\n")
    capture.release()


@app.get("/video_feed")
def video_feed():
    return StreamingResponse(generate_frames(), media_type="multipart/x-mixed-replace; boundary=frame")


# def load_image(url):
#     cap = cv2.VideoCapture(url, cv2.CAP_FFMPEG)
#
#     width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))  # float `width`
#     height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))  # float `height`
#     #
#     # buffer = cv2.VideoWriter('filename.avi',
#     #                          cv2.VideoWriter_fourcc(*'MJPG'),
#     #                          20, (width, height))
#
#     while True:
#         ret, frame = cap.read()
#         cv2.imshow('video feed', frame)
#         # buffer.write(frame)
#
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break
#
#     cap.release()
#     cv2.destroyAllWindows()

