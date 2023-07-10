import ffmpeg

import dash
from dash import html
import dash_bootstrap_components as dbc
from flask import Flask, Response
import sys

sys.path.append("yolov7")
from processing import *

server = Flask(__name__)
app = dash.Dash(__name__, server=server, external_stylesheets=[dbc.themes.BOOTSTRAP])

def generate_frames(main):
    """Получение и обработка потока"""
    capture = cv2.VideoCapture(main, cv2.CAP_FFMPEG)
    while True:
        ret, frame = capture.read()
        if not ret:
            break
        # pred, list_of_coords = make_pose_prediction(model, frame)
        # hands = Boxlos()
        # shoe = ShoesLos()
        # # box_list = gg.find(frame, list_of_coords)
        # box_list = get_bb(frame, list_of_coords) + hands.find(frame, list_of_coords) + shoe.find(frame, list_of_coords)
        #
        # # plot_pose_prediction(frame, pred, show_bbox=True)
        # plot_wear_prediction(frame, box_list)

        _, jpeg = cv2.imencode(".jpg", frame)
        frame_bytes = jpeg.tobytes()
        print(frame_bytes)
        yield (b"--frame\r\n"
               b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n\r\n")
    capture.release()


def read_video_frames(video_path):
    # Открываем видеофайл
    input_stream = ffmpeg.input(video_path)

    # Читаем видеопоток и преобразуем его в байты
    frame_bytes = (
        ffmpeg.output(input_stream, 'pipe:', format='rawvideo', pix_fmt='rgb24')
        .run(capture_stdout=True)
    )
    print(frame_bytes)
    return frame_bytes


@server.route('/video_feed')
def video_feed():
    """Функция обработки и отдачи потока"""
    return Response(generate_frames(config.URL),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


app.layout = html.Div([
    html.H1("Webcam Test"),
    html.Img(src="/video_feed")
])

if __name__ == '__main__':
    # app.run_server(debug=True, port=5000, host='0.0.0.0')
    app.run_server(debug=True, port=8050, host='127.0.0.1')
