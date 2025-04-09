#!/bin/bash
set -e

# Aktualizacja systemu
sudo apt update && sudo apt upgrade -y

# Instalacja Dockera, jeśli nie jest zainstalowany
if ! command -v docker &> /dev/null; then
  echo "Docker nie został znaleziony. Instalacja..."
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
  echo "Docker został zainstalowany. Może być konieczne ponowne zalogowanie."
fi

# Ścieżka do pliku z obrazem
IMAGE_TAR="hexapod-prod.tar"

if [ ! -f "$IMAGE_TAR" ]; then
  echo "Plik $IMAGE_TAR nie został znaleziony. Upewnij się, że znajduje się w tym katalogu."
  exit 1
fi

# Import obrazu Docker
echo "Importowanie obrazu Docker z $IMAGE_TAR..."
docker load -i "$IMAGE_TAR"
# Zmiana właściciela pliku obrazu, aby użytkownik miał do niego pełny dostęp
sudo chown $USER:$USER "$IMAGE_TAR"

# Ustawienie xhost, aby Docker mógł używać X11
xhost +local:docker

# Uruchomienie kontenera produkcyjnego
sudo docker run -it --rm \
  --name hexapod-prod \
  --network host \
  -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  hexapod-prod
