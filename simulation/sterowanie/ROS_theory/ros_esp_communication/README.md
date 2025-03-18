# **ROS-ESP WebSocket Communication Setup**

This guide explains how to set up the WebSocket communication system between **ESP32** and **ROS 2 Jazzy**.

## **Folder Structure** - _make sure your code structure looks the same!_

### ESP32 Code (PlatformIO Project)

```
ros_esp_communication/
├── esp/
│   ├── main.cpp
│   └── platformio.ini
└── ros/
    ├── __init__.py
    ├── websocket_server_echo.py - code for server testing!
    └── websocket_server.py
```

### ROS 2 WebSocket Code

```
~/ros2_ws/src/
├── ros2_websocket/
│   ├── __init__.py
│   ├── websocket_server_echo.py
│   └── websocket_server.py
└── setup.py
```

### PlatformIO Project (ESP32)

```
~/Documents/PlatformIO/Projects/Ros2 communication/
├── users.code-workspace
├── include/
├── lib/
├── platformio.ini
├── src/
│   └── main.cpp
└── test/
```

---

## Wiring
      +--------------------+
      |      Joystick      |
      |  (Analog Module)   |
      +--------------------+
       |  GND -> GND (ESP32)
       |  VCC -> 3.3V (ESP32)
       |  VRX -> GPIO4
  --------------------------------
      +---------------------+
      |        ESP32        |
      +---------------------+
       | GPIO15 -> LED1 (+)
       | GPIO16 -> LED2 (+)
       | GPIO17 -> LED3 (+)
       | GND -> Common Ground
  --------------------------------
      +--------------------------------+
      |      LEDs (x3) + resystors     |
      +--------------------------------+


## **Step-by-Step Setup**

### **Step 1: Install ROS 2 Jazzy**
Follow the official [ROS 2 Jazzy installation guide](https://docs.ros.org/en/jazzy/Installation.html).

### **Step 2: Set Up ROS 2 Package**

1. Navigate to your ROS 2 workspace:

   ```sh
   cd ~/ros2_ws/src
   ```

2. Create a new ROS 2 package:

   ```sh
   ros2 pkg create --build-type ament_python ros2_websocket
   ```

### **Step 3: Install Dependencies**
Install the `websockets` Python library:

```sh
pip install websockets
```

### **Step 4: Add WebSocket Server Code**

1. Navigate to `ros2_websocket`:

   ```sh
   cd ~/ros2_ws/src/ros2_websocket
   ```

2. Add the WebSocket server code inside the `ros2_websocket` folder. Create `websocket_server.py`:

   ```sh
   nano ros2_websocket/websocket_server.py
   ```

3. Copy and paste the WebSocket server code into the file and save it.

### **Step 5: Make the Script Executable**

```sh
chmod +x ros2_websocket/websocket_server.py
```

### **Step 6: Update `setup.py`**

1. Open `setup.py`:

   ```sh
   nano setup.py
   ```

2. Add this entry in the `entry_points` section:

   ```python
   entry_points={
       'console_scripts': [
           'websocket_server = ros2_websocket.websocket_server:main',
       ],
   },
   ```

3. Save and exit.

### **Step 7: Build the Package**

Build the ROS 2 package:

```sh
cd ~/ros2_ws
colcon build --packages-select ros2_websocket
```

### **Step 8: Source the ROS 2 Environment**

Before running the server, source your ROS 2 workspace:

```sh
source ~/ros2_ws/install/setup.bash
```

(Use `source ~/ros2_ws/install/setup.zsh` if you're using `zsh`.)

### **Step 9: Run the WebSocket Server**

Start the WebSocket server:

```sh
ros2 run ros2_websocket websocket_server
```

You should see output confirming that the WebSocket server is running.

---

### **ESP32 Setup**

#### 1. **Install PlatformIO**

If you don’t have PlatformIO, install it via [PlatformIO Installation Guide](https://platformio.org/install).

#### 2. **Configure Wi-Fi**

Open `main.cpp` in the `esp` folder and modify the Wi-Fi credentials:

```cpp
const char* ssid = "YOUR_SSID";        
const char* password = "YOUR_PASSWORD"; 
```

#### 3. **Upload Code to ESP32**

In PlatformIO, select the correct board and upload the code:

```sh
pio run --target upload
```

#### 4. **Monitor ESP32**

Open a serial monitor to check ESP32 logs:

```sh
pio device monitor
```

### **Testing Communication**

1. Power on your ESP32 device and ensure it connects to the Wi-Fi.
2. Run the WebSocket server on ROS 2 using the command:

   ```sh
   ros2 run ros2_websocket websocket_server
   ```

3. Verify that the ESP32 and ROS 2 are communicating correctly by observing the logs on both ends.

---

## **Testing WebSocket Connection**

1. Install `wscat` to test the WebSocket connection:

   ```sh
   npm install -g wscat
   ```

2. Connect to the WebSocket server:

   ```sh
   wscat -c ws://localhost:8765
   ```

3. Send a message and verify the server echoes it back.

---

## **Troubleshooting**

1. **ESP32 Connection Issues:**
   - Double-check Wi-Fi credentials in `main.cpp`.
   - Ensure ESP32 is within Wi-Fi range.

2. **ROS Server Issues:**
   - Ensure WebSocket server is running and listening on port `8765`.
   - Verify ESP32 and ROS are on the same network.
