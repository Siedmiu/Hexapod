import websocket
import json
import time

print("Connected to WebSocket server")

ws = websocket.WebSocket()
ws.connect("ws://192.168.0.123:8765")  # IP ESP32

angles = {
    "theta1": 30,
    "theta2": 60,
    "theta3": 120
}

ws.send(json.dumps(angles))
ws.close()