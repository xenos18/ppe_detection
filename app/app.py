# import uvicorn
# from fastapi import FastAPI, Request
# import cv2
# from fastapi.responses import StreamingResponse
# from fastapi.templating import Jinja2Templates
# from fastapi.responses import HTMLResponse
#
# import config
#
# import sys
#
# sys.path.append("yolov7")
# from yolov7 import *
#
# app = FastAPI()
#
#
# def generate_frames():
#     capture = cv2.VideoCapture(config.URL, cv2.CAP_FFMPEG)
#     while True:
#         ret, frame = capture.read()
#         if not ret:
#             break
#         # Обработайте кадр, если это необходимо
#         # Например, преобразуйте его в формат JPEG для передачи через HTTP
#         pred = make_pose_prediction(model, frame)
#         plot_pose_prediction(frame, pred, show_bbox=True)
#
#         _, jpeg = cv2.imencode(".jpg", frame)
#         frame_bytes = jpeg.tobytes()
#         yield (b"--frame\r\n"
#                b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n\r\n")
#     capture.release()
#
#
# templates = Jinja2Templates(directory="templates")
#
#
# @app.get("/item", response_class=HTMLResponse)
# async def read_item(request: Request):
#     return templates.TemplateResponse("main.html", {"request": request})
#
#
# @app.get("/video_feed")
# def video_feed():
#     return StreamingResponse(generate_frames(), media_type="multipart/x-mixed-replace; boundary=frame")
#
#
# if __name__ == '__main__':
#     uvicorn.run(app, port=8500)

import dash
from dash import html
from flask import Flask, Response
import sys
sys.path.append("yolov7")
from processing import *


server = Flask(__name__)
app = dash.Dash(__name__, server=server)


@server.route('/video_feed')
def video_feed():
    """Функция обработки и отдачи потока"""
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


app.layout = html.Div([
    html.H1("Webcam Test"),
    html.Img(src="/video_feed")
])

if __name__ == '__main__':
    app.run_server(debug=True)
