#!/bin/bash

# ESP32 IP - first argument
ESP_IP="$1"

if [ -z "$ESP_IP" ]; then
  echo "Usage: $0 <ESP_IP_Address>"
  exit 1
fi

# Terminal 1: ROS 2 Launch
gnome-terminal --title="ROS2 Hexapod Launch" -- bash -c "
cd ~/Hexapod/sim_and_real/ros2_ws_hex;
source install/setup.bash;
echo 'Launching hexapod in real mode with walking enabled...';
ros2 launch hex_gz main.launch.py mode:=real;
exec bash
"

# Terminal 2: WebSocket Test Client using websocat
gnome-terminal --title="WebSocket Client to ESP32" -- bash -c "
echo 'Connecting to ESP32 WebSocket Server at ws://$ESP_IP/';
websocat ws://$ESP_IP/;
exec bash
"

# Terminal 3: IMU topic run
gnome-terminal --title="IMU=" -- bash -c "
cd ~/Hexapod/sim_and_real/ros2_ws_hex;
source install/setup.bash;
echo 'IMU';
ros2 run hex_gz imu_processer.py;
exec bash
"
