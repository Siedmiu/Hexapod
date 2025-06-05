# README - Hexapod

## Introduction

Docker is a container virtualization tool that allows running applications in an isolated environment, similar to a virtual machine but with lower overhead and better integration with the host OS. Thanks to Docker, this project:
- Enables easy building of consistent production and development environments
- Isolates software dependencies
- Facilitates switching between different configurations without affecting the host system
- Supports MoveIt/RViz environments alongside Gazebo simulation.

# Project Containerization

## Differences between Production and Development Containers

Production container (based on Dockerfile.prod):
- Automatically starts the application or simulation on launch. By default, it starts the Gazebo simulation; passing "moveit" activates the MoveIt/RViz mode.
- Automatically updates the repository to the latest version on each run
- Contains full system configuration, ROS2, and dependencies required for simulation.
- Intended for deployment and demonstration of the stable application.
- Typically run with GUI support via X11.

Development container (based on Dockerfile.dev):
- Launches an interactive shell (bash) for easy debugging and testing.
- Mounts the local working directory (`Hexapod-ROS2-System`), allowing code modifications without rebuilding the image.
- Configured mainly for development work with quick code iteration.

## Usage

1. To build and run the production container (use  if needed):
   - `./build-prod.sh` – build the image and start Gazebo.
   - `./build-prod.sh moveit` – build the image and start MoveIt.
   - `./run-prod.sh` – pull the production image from Docker Hub.

2. To set up the development environment (use  if needed):
   - `./build-dev.sh` – pull the repository, build the workspace, and start the development container.
   - `./run-dev.sh` – pull the development image from Docker Hub.

3. To push images to Docker Hub:
   - `./push-to-dockerhub.sh` – interactively select prod, dev, or both and push images.

**Note:** The production container automatically pulls the latest changes from the repository on each run. The development container uses local code from the mounted directory.

3. Inside the development environment, you can launch:
   - Gazebo:
     - `ros2 launch hex_gz gazebo.launch.py`
   - RViz/MoveIt:
     - `ros2 launch hexapod_moveit_config demo.launch.py`

3. Docker Hub vs. Local Build:
   - **build-prod.sh and build-dev.sh scripts**: Build images locally from the latest [Hexapod-ROS2-System](https://github.com/Siedmiu/Hexapod-ROS2-System) repository
   - **run-prod.sh and run-dev.sh scripts**: Pull pre-built images from Docker Hub (`natantulo/hexapod:prod` and `natantulo/hexapod:dev`)
   - **Local export** (optional):
     - `docker save -o hexapod-prod.tar hexapod-prod`
     - `docker save -o hexapod-dev.tar hexapod-dev`
     - `docker load -i hexapod-prod.tar`

## Additional Information and Tips

- **Script Permissions**: If you encounter "Permission denied", make the scripts executable:
  ```bash
  chmod +x *.sh
  ```
- To run GUI containers, ensure you execute `xhost +local:docker` to allow X11 access.
- In some cases, after installing Docker, you may need to log out and back in or restart the system for group changes to take effect.
- Scripts use sudo, so you must have the appropriate privileges.
- If you see a lock icon on a file or folder, change its ownership:
  `chown -R $USER:$USER <file_or_folder>`
- To clean up unused Docker build data and system resources:
  - `docker builder prune --all` – remove unused build data.
  - `docker system prune --all --volumes` – remove unused containers, images, networks, and volumes.
- To open an additional terminal for a running container:
  - Run the container detached: `docker run -d -it <image_id>`
  - Check the container ID: `docker ps`
  - Open the first terminal with: `docker exec -it <container_id> bash`
  - Then open another terminal and repeat `docker exec ...` to get another interactive session.

## Scripts

- build-prod.sh: Builds the production image using Dockerfile.prod and runs the container with GUI.
- run-prod.sh: Pulls the production image from Docker Hub (`natantulo/hexapod:prod`) and runs the container.
- build-dev.sh: Builds the development image using Dockerfile.dev with the project directory mounted and runs the container.
- run-dev.sh: Pulls the development image from Docker Hub (`natantulo/hexapod:dev`) and runs the container.
- push-to-dockerhub.sh: Tags local images (hexapod-prod, hexapod-dev) and pushes them to Docker Hub.

## Dockerfiles

- Dockerfile.prod: Defines the production environment with ROS2, Gazebo, MoveIt, and additional tools.
- Dockerfile.dev: Defines the development environment, which automatically sources necessary scripts upon shell launch.

## GPU Support

Scripts automatically detect available GPUs (NVIDIA, AMD, Intel) and configure the container for hardware acceleration.

To manually verify GPU acceleration, use the `diagnose` argument:
```bash
./build-prod.sh diagnose
./build-dev.sh diagnose
```