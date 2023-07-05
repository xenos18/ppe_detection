import cv2
import os
from dotenv import load_dotenv

load_dotenv()

CAMERA_LOGIN = os.environ['CAMERA_LOGIN']
CAMERA_PASSWORD = os.environ['CAMERA_PASSWORD']

URL = f'rtsp://{CAMERA_LOGIN}:{CAMERA_PASSWORD}@192.168.1.108:554/cam/realmonitor?channel=1&subtype=0'


def load_image():
    cap = cv2.VideoCapture(URL, cv2.CAP_FFMPEG)

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))  # float `width`
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))  # float `height`

    buffer = cv2.VideoWriter('filename.avi',
                             cv2.VideoWriter_fourcc(*'MJPG'),
                             20, (width, height))

    while True:
        ret, frame = cap.read()
        cv2.imshow('video feed', frame)
        buffer.write(frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    load_image()
