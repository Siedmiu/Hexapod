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

# OPCJONALNE: Pobranie kodu i budowa workspace, jeśli katalog Hexapod nie istnieje
if [ ! -d "$PWD/Hexapod" ]; then
  echo "Katalog Hexapod nie znaleziony. Klonowanie repozytorium i budowa workspace..."
  git clone https://github.com/Siedmiu/Hexapod.git
  # Ustawienie właściciela repozytorium i nadanie pełnych uprawnień
  sudo chown -R $USER:$USER Hexapod
  sudo chmod -R u+rw Hexapod
  cd Hexapod/simulation/ros2_ws_hex
  bash -c "source /opt/ros/jazzy/setup.bash && colcon build"
  cd ../..
fi

# Ustawienie xhost, aby Docker mógł używać X11 
xhost +local:docker

# Budowanie obrazu DEV (Dockerfile.dev znajduje się w tym samym katalogu)
docker build -t hexapod-dev -f "$(dirname "$0")/Dockerfile.dev" .

# Uruchomienie kontenera DEV z zamontowanym katalogiem Hexapod bez automatycznego launch’u
docker run -it --rm \
  --name hexapod-dev \
  --network host \
  -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -v "$PWD/Hexapod:/ros_ws/Hexapod" \
  hexapod-dev \
  bash -c "source /opt/ros/jazzy/setup.bash && bash"