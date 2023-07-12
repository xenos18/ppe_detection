import random

import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from flask import Flask, Response
import subprocess

from processing import *

server = Flask(__name__)
app = dash.Dash(__name__, server=server, external_stylesheets=[dbc.themes.BOOTSTRAP])
server.human = 3

url = 'https://camera.lipetsk.ru/ms-31.camera.lipetsk.ru/live/4c1f5405-e8a9-4d38-9bbd-6066946fb022/playlist.m3u8'


def get_video_stream():
    ffmpeg_command = [
        'ffmpeg',
        '-i', f'{url}',  # Замените ссылку на фактическую ссылку видеопотока
        '-c:v', 'libx264',
        '-f', 'image2pipe',
        '-pix_fmt', 'rgb24',
        '-vcodec', 'rawvideo',
        '-']

    ffmpeg_process = subprocess.Popen(ffmpeg_command, stdout=subprocess.PIPE, bufsize=10 ** 8)

    while True:
        frame = ffmpeg_process.stdout.read(
            640 * 480 * 3)  # Размер кадра, подстраивайте под требования вашего видеопотока

        if not frame:
            break

        yield b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n'

    ffmpeg_process.stdout.flush()
    ffmpeg_process.kill()


def generate_frames():
    capture = cv2.VideoCapture(config.URL, cv2.CAP_FFMPEG)
    while True:
        ret, frame = capture.read()
        if not ret:
            break
        # Обработайте кадр, если это необходимо
        # Например, преобразуйте его в формат JPEG для передачи через HTT
        server.human = server.human + 1
        _, jpeg = cv2.imencode(".jpg", frame)
        frame_bytes = jpeg.tobytes()
        yield (b"--frame\r\n"
               b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n\r\n")
    capture.release()


def generate_image():
    while True:

        print(server.human)
        yield (b"--frame\r\n"
               b"Content-Type: image/jpeg\r\n\r\n" + b"\r\n\r\n")


@server.route('/video_feed')
def video_feed():
    """Функция обработки и отдачи потока"""
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@server.route('/image_feed')
def image_feed():
    """Функция обработки и отдачи потока"""
    return Response(generate_image(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


app.layout = html.Div(
    children=[
        html.Div(className='header', children=[
            dbc.Row(
                children=[
                    dbc.Col(
                        html.Img(src='static/img/logo.png', className='logo', style={"width": "40%"}),
                        width=3
                    ),
                    dbc.Col(
                        dbc.Button("Настройки", color='primary', className='button',
                                   style={"float": "left", 'padding-top': '0.5em'}),
                        width=3
                    ),
                ],
                align='center',
                justify='center',
                style={'padding': '0.7em'}
            ),
        ]),
        html.Img(src="/video_feed",
                 style={"width": "70%", "float": "left", 'padding': '1.5em', 'padding-top': '0.5em', }),
    ]

)


if __name__ == '__main__':
    # app.run_server(debug=True, port=5000, host='0.0.0.0')
    app.run_server(debug=True, port=8030, host='127.0.0.1')
