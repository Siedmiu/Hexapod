#!/bin/bash
set -e

# Check if DISPLAY variable is set
if [ -z "$DISPLAY" ]; then
    echo "DISPLAY variable is not set. Exiting."
    exit 1
fi

# Function to install packages if missing
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

# Update system and install core tools
sudo apt update || true
install_if_missing pciutils x11-xserver-utils curl ca-certificates gnupg

# Check if xhost is available
if ! command -v xhost &> /dev/null; then
    echo "xhost command not found. This should not happen after installing x11-xserver-utils."
    echo "Please ensure x11-xserver-utils is installed correctly."
    exit 1
fi

# Install Docker if not found
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
  if ! getent group docker > /dev/null; then
    sudo groupadd docker
  fi
  sudo usermod -aG docker $USER
  echo "Docker has been installed. You may need to log out and log back in."
  echo "If you don't want to reboot/re-login now, you can try 'newgrp docker' in this terminal session."
fi

# Configure X11 and hardware acceleration
DOCKER_RUN_ARGS_GUI=""
DOCKER_GPU_ARGS=""

# Setting xhost so Docker can use X11
xhost +local:docker

# Configure Xauthority for secure X11 forwarding
XAUTH_FILE=$(mktemp /tmp/.docker.xauth.import-prod.XXXXXX)
trap 'rm -f "$XAUTH_FILE"' EXIT

touch "$XAUTH_FILE"
xauth_list=$(xauth nlist "${DISPLAY}")
if [ -n "$xauth_list" ]; then
    echo "$xauth_list" | sed -e 's/^..../ffff/' | xauth -f "$XAUTH_FILE" nmerge -
else
    echo "Warning: 'xauth nlist ${DISPLAY}' returned empty. X11 forwarding may not work correctly."
fi
chmod a+r "$XAUTH_FILE"

DOCKER_RUN_ARGS_GUI+=" --env=DISPLAY=$DISPLAY"
DOCKER_RUN_ARGS_GUI+=" --env=QT_X11_NO_MITSHM=1"
DOCKER_RUN_ARGS_GUI+=" --volume=/tmp/.X11-unix:/tmp/.X11-unix:rw"
DOCKER_RUN_ARGS_GUI+=" --env=XAUTHORITY=$XAUTH_FILE"
DOCKER_RUN_ARGS_GUI+=" --volume=$XAUTH_FILE:$XAUTH_FILE:rw"

echo "Detecting GPU..."
if lspci | grep -iq nvidia; then
    echo "Nvidia GPU detected."
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
        echo "AMD/ATI GPU detected."
    elif lspci | grep -iqE 'vga.*intel|graphics.*intel'; then
        echo "Integrated Intel GPU detected."
    fi
    echo "Mounting /dev/dri and adding to 'video' group."
    install_if_missing mesa-utils libgl1-mesa-dri
    DOCKER_GPU_ARGS="--device=/dev/dri --group-add video"
    if [ -e /dev/dri/card0 ]; then
        if [ ! -r /dev/dri/card0 ] || [ ! -w /dev/dri/card0 ]; then
            echo "Warning: No read/write permissions for /dev/dri/card0."
            echo "You may need to add the user to 'render' or 'video' group on the host: sudo usermod -aG render \$USER && sudo usermod -aG video \$USER"
            echo "After adding to the group, log out and log back in, or run 'newgrp render' and 'newgrp video' in a new terminal session."
        fi
    else
        echo "Warning: /dev/dri/card0 not found. Hardware acceleration may not work."
    fi
else
    echo "No supported GPU detected (Nvidia, AMD, Intel) or lspci is not available."
    echo "Hardware acceleration may not work correctly."
    if [ -d "/dev/dri" ]; then
        echo "Found /dev/dri. Attempting to mount. This may work for some open-source drivers."
        DOCKER_GPU_ARGS="--device=/dev/dri --group-add video"
    fi
fi

# Pulling production image from Docker Hub
echo "Pulling production image from Docker Hub..."
sudo docker pull natantulo/hexapod:prod

# Tagging image locally for consistency with other scripts
sudo docker tag natantulo/hexapod:prod hexapod-prod

# Check if user wants diagnostic mode
if [ "$1" == "diagnose" ]; then
  echo "Starting production container in diagnostic mode..."
  sudo docker run -it --rm \
    --name hexapod-prod-diag \
    --network host \
    $DOCKER_RUN_ARGS_GUI \
    $DOCKER_GPU_ARGS \
    hexapod-prod \
    bash -c "cd /root/Hexapod-ROS2-System && git pull && cd sim_and_real/ros2_ws_hex && source /opt/ros/jazzy/setup.bash && colcon build && if [ -f /root/Hexapod-ROS2-System/Docker/check-gpu.sh ]; then /root/Hexapod-ROS2-System/Docker/check-gpu.sh; else echo 'Diagnostic script does not exist'; fi && source /opt/ros/jazzy/setup.bash && source /root/Hexapod-ROS2-System/sim_and_real/ros2_ws_hex/install/setup.bash && bash"
  exit 0
fi

# Add mode selection: default Gazebo, 'moveit' triggers MoveIt mode
if [ "$1" == "moveit" ]; then
    LAUNCH_CMD="ros2 launch hexapod_moveit_config demo.launch.py"
else
    LAUNCH_CMD="ros2 launch hex_gz gazebo.launch.py"
fi

# Run production container with automatic repository update
sudo docker run -it --rm \
  --name hexapod-prod \
  --network host \
  $DOCKER_RUN_ARGS_GUI \
  $DOCKER_GPU_ARGS \
  hexapod-prod \
  bash -c "cd /root/Hexapod-ROS2-System && echo 'Updating repository...' && git pull && \
    cd sim_and_real/ros2_ws_hex && echo 'Building workspace...' && \
    source /opt/ros/jazzy/setup.bash && colcon build && \
    echo 'Starting simulation...' && source /opt/ros/jazzy/setup.bash && \
    source /root/Hexapod-ROS2-System/sim_and_real/ros2_ws_hex/install/setup.bash && \
    nohup ros2 run hex_gz ws_run.py & \
    sleep 5 && \
    echo 'Launching main command...' && \
    source /opt/ros/jazzy/setup.bash && \
    source /root/Hexapod-ROS2-System/sim_and_real/ros2_ws_hex/install/setup.bash && \
    $LAUNCH_CMD"