from flask import Flask, render_template, Response
from processing import read_frames, generate_frames
from config import URL

app = Flask(__name__)


@app.route('/video_feed')
def video_feed():
    """Функция обработки и отдачи потока"""
    return Response(read_frames(URL),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/')
def hello():
    return render_template('main.html')


if __name__ == '__main__':
    app.run()
