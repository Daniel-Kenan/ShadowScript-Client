import asyncio
import websockets

async def connect_as_master():
    # Replace these values with the actual server address and port
    server_address = "ws://localhost:8765"
    user_name = input("Enter your name: ")
    room = input("Enter the room: ")
    user_type = "master"
    master_code = input("Enter the master code: ")

    # Connect to the WebSocket server
    async with websockets.connect(server_address) as websocket:
        # Send user information and master code to the server
        await websocket.send(f"{user_name},{room},{user_type},{master_code}")
        
        # Receive and print the welcome message from the server
        welcome_message = await websocket.recv()
        print(welcome_message)

        # Start the event loop for sending and receiving messages
        while True:
            message = input("Enter your message (or 'exit' to quit): ")
            
            if message.lower() == 'exit':
                break

            # Send the message to the server
            await websocket.send(message)

# Run the master client
asyncio.get_event_loop().run_until_complete(connect_as_master())
