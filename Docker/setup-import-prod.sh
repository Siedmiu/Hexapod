#!/bin/bash
set -e

# Sprawdzenie, czy zmienna DISPLAY jest ustawiona
if [ -z "$DISPLAY" ]; then
    echo "DISPLAY variable is not set. Exiting."
    exit 1
fi

# Funkcja do instalacji pakietów, jeśli nie są zainstalowane
install_if_missing() {
    for pkg in "$@"; do
        if ! dpkg -s "$pkg" &> /dev/null; then
            echo "$pkg is not installed. Installing..."
            sudo apt install -y "$pkg"
        else
            echo "$pkg is already installed."
        fi
    done
}

# Aktualizacja systemu i instalacja podstawowych narzędzi
sudo apt update || true
install_if_missing pciutils x11-xserver-utils curl ca-certificates gnupg

# Sprawdzenie, czy xhost jest dostępny
if ! command -v xhost &> /dev/null; then
    echo "xhost command not found. This should not happen after installing x11-xserver-utils."
    echo "Please ensure x11-xserver-utils is installed correctly."
    exit 1
fi

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
  if ! getent group docker > /dev/null; then
    sudo groupadd docker
  fi
  sudo usermod -aG docker $USER
  echo "Docker został zainstalowany. Może być konieczne ponowne zalogowanie."
  echo "If you don't want to reboot/re-login now, you can try 'newgrp docker' in this terminal session."
fi

# Konfiguracja X11 i akceleracji sprzętowej
DOCKER_RUN_ARGS_GUI=""
DOCKER_GPU_ARGS=""

# Ustawienie xhost, aby Docker mógł używać X11
xhost +local:docker

# Konfiguracja Xauthority dla bezpieczniejszego przekierowania X11
XAUTH_FILE=$(mktemp /tmp/.docker.xauth.import-prod.XXXXXX)
trap 'rm -f "$XAUTH_FILE"' EXIT

touch "$XAUTH_FILE"
xauth_list=$(xauth nlist "${DISPLAY}")
if [ -n "$xauth_list" ]; then
    echo "$xauth_list" | sed -e 's/^..../ffff/' | xauth -f "$XAUTH_FILE" nmerge -
else
    echo "Ostrzeżenie: Polecenie 'xauth nlist ${DISPLAY}' zwróciło pusty wynik. Przekierowanie X11 z Xauthority może nie działać poprawnie."
fi
chmod a+r "$XAUTH_FILE"

DOCKER_RUN_ARGS_GUI+=" --env=DISPLAY=$DISPLAY"
DOCKER_RUN_ARGS_GUI+=" --env=QT_X11_NO_MITSHM=1"
DOCKER_RUN_ARGS_GUI+=" --volume=/tmp/.X11-unix:/tmp/.X11-unix:rw"
DOCKER_RUN_ARGS_GUI+=" --env=XAUTHORITY=$XAUTH_FILE"
DOCKER_RUN_ARGS_GUI+=" --volume=$XAUTH_FILE:$XAUTH_FILE:rw"

echo "Wykrywanie GPU..."
if lspci | grep -iq nvidia; then
    echo "Wykryto kartę GPU Nvidia."
    if ! dpkg -s nvidia-container-toolkit &> /dev/null; then
        echo "nvidia-container-toolkit is not installed. Installing..."
        curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \
          && curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
            sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
            sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list > /dev/null
        sudo apt update
        install_if_missing nvidia-container-toolkit
        sudo nvidia-ctk runtime configure --runtime=docker
        echo "nvidia-container-toolkit installed. Restarting Docker service..."
        sudo systemctl restart docker
        echo "Docker service restarted. You might need to re-run this script if the restart was too slow."
    else
        echo "nvidia-container-toolkit is already installed."
    fi
    DOCKER_GPU_ARGS="--runtime=nvidia --gpus all"
    DOCKER_RUN_ARGS_GUI+=" --env=__NV_PRIME_RENDER_OFFLOAD=1"
    DOCKER_RUN_ARGS_GUI+=" --env=__GLX_VENDOR_LIBRARY_NAME=nvidia"
    DOCKER_RUN_ARGS_GUI+=" --env=NVIDIA_VISIBLE_DEVICES=all"
    DOCKER_RUN_ARGS_GUI+=" --env=NVIDIA_DRIVER_CAPABILITIES=all"
    if [ -d "/usr/lib/nvidia" ]; then
        DOCKER_GPU_ARGS+=" --volume=/usr/lib/nvidia:/usr/lib/nvidia:ro"
    fi
elif lspci | grep -iqE 'vga.*amd|vga.*ati|radeon|vga.*intel|graphics.*intel'; then
    if lspci | grep -iqE 'vga.*amd|vga.*ati|radeon'; then
        echo "Wykryto kartę GPU AMD/ATI."
    elif lspci | grep -iqE 'vga.*intel|graphics.*intel'; then
        echo "Wykryto zintegrowaną kartę graficzną Intel."
    fi
    echo "Montowanie /dev/dri i dodawanie do grupy 'video'."
    install_if_missing mesa-utils libgl1-mesa-dri
    DOCKER_GPU_ARGS="--device=/dev/dri --group-add video"
    if [ -e /dev/dri/card0 ]; then
        if [ ! -r /dev/dri/card0 ] || [ ! -w /dev/dri/card0 ]; then
            echo "Ostrzeżenie: Brak uprawnień do odczytu/zapisu dla /dev/dri/card0."
            echo "Może być konieczne dodanie użytkownika do grupy 'render' lub 'video' na hoście: sudo usermod -aG render \$USER && sudo usermod -aG video \$USER"
            echo "Po dodaniu do grupy, wyloguj się i zaloguj ponownie, lub uruchom 'newgrp render' i 'newgrp video' w nowej sesji terminala."
        fi
    else
        echo "Ostrzeżenie: Nie znaleziono /dev/dri/card0. Akceleracja sprzętowa dla AMD/Intel może nie działać."
    fi
else
    echo "Nie wykryto wspieranej karty GPU (Nvidia, AMD, Intel) lub lspci nie jest dostępne."
    echo "Akceleracja sprzętowa może nie działać poprawnie."
    if [ -d "/dev/dri" ]; then
        echo "Znaleziono /dev/dri. Próba montowania. Może to zadziałać dla niektórych sterowników open-source."
        DOCKER_GPU_ARGS="--device=/dev/dri --group-add video"
    fi
fi

# Ścieżka do pliku z obrazem
IMAGE_TAR="hexapod-prod.tar"

if [ ! -f "$IMAGE_TAR" ]; then
  echo "Plik $IMAGE_TAR nie został znaleziony. Upewnij się, że znajduje się w tym katalogu."
  exit 1
fi

# Import obrazu Docker
echo "Importowanie obrazu Docker z $IMAGE_TAR..."
sudo docker load -i "$IMAGE_TAR"
sudo chown $USER:$USER "$IMAGE_TAR"

# Sprawdzanie czy użytkownik chce tryb diagnostyczny
if [ "$1" == "diagnose" ]; then
  echo "Uruchamianie kontenera produkcyjnego w trybie diagnostycznym..."
  sudo docker run -it --rm \
    --name hexapod-prod-diag \
    --network host \
    $DOCKER_RUN_ARGS_GUI \
    $DOCKER_GPU_ARGS \
    hexapod-prod \
    bash -c "cd /root/Hexapod && git pull && cd sim_and_real/ros2_ws_hex && source /opt/ros/jazzy/setup.bash && colcon build && if [ -f /root/Hexapod/Docker/check-gpu.sh ]; then /root/Hexapod/Docker/check-gpu.sh; else echo 'Skrypt diagnostyczny nie istnieje'; fi && source /opt/ros/jazzy/setup.bash && source /root/Hexapod/sim_and_real/ros2_ws_hex/install/setup.bash && bash"
  exit 0
fi

# Dodanie wyboru trybu: domyślnie Gazebo, jeśli podamy "moveit" to tryb MoveIt
if [ "$1" == "moveit" ]; then
    LAUNCH_CMD="ros2 launch hexapod_moveit_config demo.launch.py"
else
    LAUNCH_CMD="ros2 launch hex_gz gazebo.launch.py"
fi

# Uruchomienie kontenera produkcyjnego z automatyczną aktualizacją repozytorium
sudo docker run -it --rm \
  --name hexapod-prod \
  --network host \
  $DOCKER_RUN_ARGS_GUI \
  $DOCKER_GPU_ARGS \
  hexapod-prod \
  bash -c "cd /root/Hexapod && echo 'Aktualizowanie repozytorium...' && git pull && cd sim_and_real/ros2_ws_hex && echo 'Budowanie workspace...' && source /opt/ros/jazzy/setup.bash && colcon build && echo 'Uruchamianie symulacji...' && source /opt/ros/jazzy/setup.bash && source /root/Hexapod/sim_and_real/ros2_ws_hex/install/setup.bash && $LAUNCH_CMD"
