#!/bin/bash
set -e

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

# Budowanie obrazu produkcyjnego
sudo docker build -t hexapod-prod -f Dockerfile.prod .

# Ustawienie xhost, aby Docker mógł używać X11 
xhost +local:docker

# Uruchomienie kontenera produkcyjnego z konfiguracją GUI
sudo docker run -it --rm \
  --name hexapod-prod \
  --network host \
  -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  hexapod-prod