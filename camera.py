import cv2
import os
from dotenv import load_dotenv

load_dotenv()

CAMERA_LOGIN = os.environ['CAMERA_LOGIN']
CAMERA_PASSWORD = os.environ['CAMERA_PASSWORD']

RTSP_URL = f'rtsp://{CAMERA_LOGIN}:{CAMERA_PASSWORD}@192.168.1.108:554/cam/realmonitor?channel=1&subtype=0'

# os.environ['OPENCV_FFMPEG_CAPTURE_OPTIONS'] = 'rtsp_transport;udp'

video = cv2.VideoCapture(RTSP_URL, cv2.CAP_FFMPEG)

if not video.isOpened():
    print('Cannot open RTSP stream')
    exit(-1)

frame_width = int(video.get(3))
frame_height = int(video.get(4))
   
size = (frame_width, frame_height)

buffer = cv2.VideoWriter('filename.avi', 
                         cv2.VideoWriter_fourcc(*'MJPG'),
                         10, size)

while True:
    try:
        ret, frame = video.read()
    
        if ret == True: 
            buffer.write(frame)
    except:
        video.release()
        break
