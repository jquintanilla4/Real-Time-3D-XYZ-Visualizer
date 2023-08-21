import asyncio
import websockets
import json
import logging
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import threading
import queue
import random
import time

logging.basicConfig(level=logging.INFO)

# Queue to store received coordinates and IDs
plot_queue = queue.Queue()

# Dictionary to store colors for different IDs
id_colors = {}

# List to store scatter plot points and their creation times
points = []

# Create a new figure for the 3D scatter plot
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.set_xlabel('X (meters)')
ax.set_ylabel('Y (meters)')
ax.set_zlabel('Z (meters)')

# Function to update the plot
def update(frame):
    global points
    current_time = time.time()

    # Remove points that are older than three seconds
    points = [(p, t) for (p, t) in points if current_time - t < 3]

    # Clear previous plot
    ax.clear()
    ax.set_xlabel('X (meters)')
    ax.set_ylabel('Y (meters)')
    ax.set_zlabel('Z (meters)')

    # Plot points, adjusting alpha based on age
    for p, t in points:
        obj_id, x, y, z = p
        color = id_colors.get(obj_id, (random.random(), random.random(), random.random()))
        id_colors[obj_id] = color
        alpha = max(0, 1 - (current_time - t) / 3)  # Fade over 3 seconds
        ax.scatter(x, y, z, c=[color], alpha=alpha)

    # Add new points
    while not plot_queue.empty():
        p = plot_queue.get()
        points.append((p, current_time))

# Set up the animation
ani = FuncAnimation(fig, update, interval=50)

async def test():
    uri = "ws://192.168.8.9:8765"
    async with websockets.connect(uri) as websocket:
        while True:
            try:
                # Set a timeout of 10 seconds for receiving a message
                message = await asyncio.wait_for(websocket.recv(), timeout=10)
                data = json.loads(message)
                logging.info(data)

                # Check if data has 'obj_id', 'x', 'y', and 'z'
                if all(key in data for key in ['obj_id', 'x', 'y', 'z']):
                    obj_id, x, y, z = data['obj_id'], data['x'], data['y'], data['z']
                    plot_queue.put((obj_id, x, y, z))
            except asyncio.TimeoutError:
                logging.warning("No data received for 10 seconds. Continuing to listen...")
            except websockets.exceptions.ConnectionClosed:
                logging.error("Unreal Engine disconnected")
                break
            except Exception as e:
                logging.error(e)
                continue

# Function to run the asyncio loop
def run_loop():
    asyncio.run(test())

# Start the asyncio loop in a separate thread
loop_thread = threading.Thread(target=run_loop)
loop_thread.start()

# Show the plot
plt.show()
