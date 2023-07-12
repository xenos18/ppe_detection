from flask import Flask, render_template, Response
from processing import generate_frames


app = Flask(__name__)


@app.route('/video_feed')
def video_feed():
    """Функция обработки и отдачи потока"""
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/')
def hello():
    return render_template('main.html')


if __name__ == '__main__':
    app.run()
