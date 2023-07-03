import argparse
import configparser
from typing import Dict, Any
import cv2
import os
import datetime
from dotenv import load_dotenv


def get_config() -> Dict[str, Any]:
    """
    Возвращает конфиг приложения по аргументам командной строки,
    config.ini и переменным окружения
    """
    config = {}

    load_dotenv()
    os.environ = {"CAMERA_LOGIN": "none", "CAMERA_PASSWORD": "none"} | os.environ
    config["camera_login"] = os.environ["CAMERA_LOGIN"]
    config["camera_password"] = os.environ["CAMERA_PASSWORD"]

    cmd_parser = argparse.ArgumentParser(
        prog='CameraReciever',
        description='Получает и сохраняет видеопоток в нужном разрешении'
    )
    cmd_parser.add_argument(
        '-c', '--config',
        default="./config.ini",
        help="Путь к конфиг-файлу",
    )
    cmd_parser.add_argument(
        '--width',
        type=int,
        help="Ширина изображения"
    )
    cmd_parser.add_argument(
        '--height',
        type=int,
        help="Высота изображения"
    )
    cmd_parser.add_argument(
        '-p', "--video_dir",
        help='Путь к папке для хранения видео'
    )
    cmd_parser.add_argument(
        '-v', '--vision',
        help='Включить окно с трансляцией видео',
        action='store_true'
    )
    cmd_parser.add_argument(
        '--camera_ip',
        help='IP-адрес камеры'
    )
    cmd_parser.add_argument(
        '--camera_port',
        help='Порт камеры'
    )
    config.update(vars(cmd_parser.parse_args()))

    cfg_path = config["config"]
    del config['config']

    cfg_parser = configparser.ConfigParser()
    cfg_parser.read_dict({"camera.reciever": {"width": 1920, "height": 1080, "video_dir": "./video/"}})
    try:
        cfg_parser.read(cfg_path)
    except FileNotFoundError:
        pass
    if not config['width']:
        config['width'] = cfg_parser['camera.reciever'].getint('width')
    if not config['height']:
        config['height'] = cfg_parser['camera.reciever'].getint('height')
    if not config['video_dir']:
        config['video_dir'] = cfg_parser['camera.reciever']['video_dir']
    if not config['camera_ip']:
        config['camera_ip'] = cfg_parser['camera.reciever']['camera_ip']
    if not config['camera_port']:
        config['camera_port'] = cfg_parser['camera.reciever']['camera_port']

    return config


def main():
    cfg = get_config()

    rtsp_url = f'rtsp://{cfg["camera_login"]}:{cfg["camera_password"]}@{cfg["camera_ip"]}:{cfg["camera_port"]}' \
               f'/cam/realmonitor?channel=1&subtype=0'

    video = cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG)

    if not video.isOpened():
        print('Cannot open RTSP stream')
        exit(-1)

    frame_width = int(video.get(3))
    frame_height = int(video.get(4))

    size = (frame_width, frame_height)

    name = f"{cfg['video_dir']}\\video_{str(datetime.datetime.now())[:-7]}.avi".replace(":", "-").replace(" ", "_")
    print(name)
    buffer = cv2.VideoWriter(name, cv2.VideoWriter_fourcc(*"MJPG"), 10, size)

    while True:
        try:
            ret, frame = video.read()

            if ret is True:
                buffer.write(frame)
                if cfg['vision']:
                    cv2.imshow("Video Capture", frame)
                    cv2.waitKey(1)
        except Exception as e:
            print(e)
            video.release()
            break


if __name__ == "__main__":
    main()
