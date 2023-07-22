from camera import camera
import asyncio
import websockets


async def main():
    async with websockets.serve(camera, "localhost", 8765):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
# def run(url):
#     camera(url)
#
#
# if __name__ == '__main__':
#     run(RTSP_URL)
