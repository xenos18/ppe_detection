import cv2
import numpy as np
import subprocess as sp
import shlex
import config

rtsp_stream0 = config.URL  # Use localhost for testing
width = 256  # Use low resolution (for testing).
height = 144
fps = 30

# https://stackoverflow.com/questions/60462840/ffmpeg-delay-in-decoding-h264
ffmpeg_cmd = shlex.split(
    f'ffmpeg -nostdin -probesize 32 -flags low_delay -fflags nobuffer -rtsp_flags listen -rtsp_transport tcp -stimeout 1000000 -an -i {rtsp_stream0} -pix_fmt bgr24 -an -vcodec rawvideo -f rawvideo pipe:')

# FFplay command before updating the code (latency is still too high):
# ffplay_cmd = shlex.split(f'ffplay -probesize 32 -analyzeduration 0 -sync ext -fflags nobuffer -flags low_delay -avioflags direct -rtsp_flags listen -strict experimental -framedrop -rtsp_transport tcp -listen_timeout 1000000 {rtsp_stream1}')

# Updated FFplay command - adding "-vf setpts=0" (fixing the latency issue):
# https://stackoverflow.com/questions/16658873/how-to-minimize-the-delay-in-a-live-streaming-with-ffmpeg


# Open sub-process that gets in_stream as input and uses stdout as an output PIPE.
process = sp.Popen(ffmpeg_cmd, stdout=sp.PIPE)  # ,stderr=sp.DEVNULL

# The following FFmpeg sub-process stream RTSP video.
# The video is synthetic video with frame counter (that counts every frame) at 30fps.
# The arguments of the encoder are almost default arguments - not tuned for low latency.
# drawtext filter with the n or frame_num function https://stackoverflow.com/questions/15364861/frame-number-overlay-with-ffmpeg
rtsp_streaming_process = sp.Popen(shlex.split(f'ffmpeg -re -f lavfi -i testsrc=size={width}x{height}:rate={fps} '
                                              '-filter_complex "drawtext=fontfile=Arial.ttf: text=''%{frame_num}'': start_number=1: x=(w-tw)/2: y=h-(2*lh): fontcolor=black: fontsize=72: box=1: boxcolor=white: boxborderw=5",'
                                              'split[v0][v1] '  # Split the input into [v0] and [v1]
                                              '-vcodec libx264 -pix_fmt yuv420p -g 30 -rtsp_transport tcp -f rtsp -muxdelay 0.1 -bsf:v dump_extra '
                                              f'-map "[v0]" -an {rtsp_stream0} '))

while True:
    raw_frame = process.stdout.read(width * height * 3)

    if len(raw_frame) != (width * height * 3):
        print('Error reading frame!!!')  # Break the loop in case of an error (too few bytes were read).
        break

    # Transform the byte read into a numpy array, and reshape it to video frame dimensions
    frame = np.frombuffer(raw_frame, np.uint8)
    frame = frame.reshape((height, width, 3))

    # Show frame for testing
    cv2.imshow('frame', frame)
    key = cv2.waitKey(1)

    if key == 27:
        break

process.stdout.close()
process.wait()
rtsp_streaming_process.kill()
cv2.destroyAllWindows()