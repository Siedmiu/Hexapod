#!/bin/bash
set -e

# Sprawdzenie, czy zmienna DISPLAY jest ustawiona
if [ -z "$DISPLAY" ]; then
    echo "DISPLAY variable is not set. Exiting."
    exit 1
fi

# Sprawdzenie, czy xhost jest dostępny
if ! command -v xhost &> /dev/null; then
    echo "xhost command not found. Please install x11-xserver-utils."
    exit 1
fi

# Aktualizacja systemu
sudo apt update && sudo apt upgrade -y

# Instalacja Dockera (jeśli nie jest zainstalowany)
if ! command -v docker &> /dev/null; then
  echo "Docker not found. Installing..."
  sudo apt install -y ca-certificates curl gnupg
  sudo install -m 0755 -d /etc/apt/keyrings
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
  echo \
    "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
    https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" \
    | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
  sudo apt update
  sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
  sudo usermod -aG docker $USER
  echo "Docker installed. You may need to reboot or log out and back in for group changes to apply."
fi

# Ustawienie xhost, aby Docker mógł używać X11 
xhost +local:docker

# Dodajemy wybór trybu: domyślnie Gazebo, jeśli podamy "moveit" to tryb MoveIt
if [ "$1" == "moveit" ]; then
    LAUNCH_CMD="ros2 launch hexapod_moveit_config demo.launch.py"  # zmieniono nazwę pakietu
else
    LAUNCH_CMD="ros2 launch hex_gz gazebo.launch.py"
fi

# Budowanie obrazu produkcyjnego
sudo docker build -t hexapod-prod -f Dockerfile.prod .

# Uruchomienie kontenera produkcyjnego z konfiguracją GUI / MoveIt
sudo docker run -it --rm \
  --name hexapod-prod \
  --network host \
  -e DISPLAY=$DISPLAY \
  -e QT_X11_NO_MITSHM=1 \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  hexapod-prod \
  bash -c "source /opt/ros/jazzy/setup.bash && source /root/Hexapod/simulation/ros2_ws_hex/install/setup.bash && $LAUNCH_CMD"