import time

import cv2
import threading
import queue
import ffmpeg
import numpy as np


class VideoCapture:
    args = {
        "rtsp_transport": "tcp",
        "fflags": "nobuffer",
        "flags": "low_delay"
    }

    prev = time.time()

    def __init__(self, name):
        self.url = name
        self.cap = cv2.VideoCapture(self.url)
        self.q = queue.Queue()

        t = threading.Thread(target=self._reader)
        t.daemon = True
        t.start()

    def _reader(self):
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break
            if not self.q.empty():
                try:
                    self.q.get_nowait()
                except queue.Empty:
                    pass
            self.q.put(frame)

    def read(self):
        # now = time.time()
        # print(f"\rSpeed: {now - self.prev}", end="")
        # self.prev = now

        return self.q.get()
    
    def ffmpeg_reader(self):
        probe = ffmpeg.probe(self.url)
        cap_info = next(x for x in probe['streams'] if x['codec_type'] == 'video')
        width = cap_info['width']
        height = cap_info['height']

        process1 = (
            ffmpeg
            .input(self.url, **self.args)
            .output('pipe:', format='rawvideo', pix_fmt='rgb24')
            .overwrite_output()
            .run_async(pipe_stdout=True)
        )

        while True:
            in_bytes = process1.stdout.read(width * height * 3)
            if not in_bytes:
                break

            in_frame = (
                np
                .frombuffer(in_bytes, np.uint8)
                .reshape([height, width, 3])
            )

            frame = cv2.cvtColor(in_frame, cv2.COLOR_RGB2BGR)

            if not self.q.empty():
                try:
                    self.q.get_nowait()
                except queue.Empty:
                    pass
            self.q.put(frame)

        process1.kill()
