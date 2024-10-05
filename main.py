from fastapi import FastAPI, WebSocket, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import serial
import json
import threading

from database import db_habdler

app = FastAPI()
global_db_handler = db_habdler()

# Global variables for temperature and RFID
rfid_global = "1234567890"  # Set your expected RFID here
temperature_value = None

# Initialize serial connection to Arduino
arduino = serial.Serial('COM3', 9600, timeout=1)  # Replace 'COM3' with your Arduino port

# List to hold active WebSocket connections
websockets: List[WebSocket] = []

# Function to broadcast data to all WebSocket clients
async def broadcast_temperature():
    global temperature_value
    for websocket in websockets:
        await websocket.send_text(json.dumps({"type": "temperature", "value": temperature_value}))

# Function to handle serial data reading from Arduino
def read_from_arduino():
    global temperature_value
    while True:
        if arduino.in_waiting > 0:
            # Read the JSON data from Arduino
            message = arduino.readline().decode().strip()
            try:
                data = json.loads(message)
                # Check if it's temperature or RFID
                if "temperature" in data:
                    temperature_value = data["temperature"]
                    # Send temperature value to WebSocket clients
                    if websockets:
                        threading.Thread(target=broadcast_temperature).start()

                elif "rfid" in data:
                    rfid_value = data["rfid"]
                    # Check if RFID matches the global variable
                    response = "true" if rfid_value == rfid_global else "false"
                    # Send response to Arduino
                    arduino.write(response.encode())
            except json.JSONDecodeError:
                print("Invalid JSON received from Arduino")

# Start the serial communication thread
threading.Thread(target=read_from_arduino, daemon=True).start()

# WebSocket endpoint to handle connections
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    websockets.append(websocket)
    try:
        while True:
            await websocket.receive_text()  # Keep the connection alive
    except:
        websockets.remove(websocket)


# Pydantic models for request validation
class UserInput(BaseModel):
    uid: str
    nombre: str
    apellido: str
    id: str
    model: str


class LoginInput(BaseModel):
    name: str
    password: str


# Example GET endpoint to get users from the database
@app.get("/get_users")
def get_users():
    users = global_db_handler.get_all_users()
    if not users:
        raise HTTPException(status_code=404, detail="No users found")
    return users


# POST endpoint for user login
@app.post("/login")
def login(input: LoginInput):
    success = global_db_handler.login(input.name, input.password)
    if not success:
        raise HTTPException(status_code=401, detail="Login failed")
    return {"message": "Login successful"}


# POST endpoint to add a new user
@app.post("/add_user")
def add_user(input: UserInput):
    success = global_db_handler.add_new_user(input.dict())
    if not success:
        raise HTTPException(status_code=400, detail="User creation failed")
    return {"message": "User created successfully"}
