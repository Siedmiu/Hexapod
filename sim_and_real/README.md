# Simulation, ROS2 and gazebo

![Screenshot](screenshots/gazebosc.png)

## Table of Contents
1. [Introduction](#introduction)
2. [Features](#features)
3. [Installation](#installation)
4. [Usage](#usage)
5. [Contributing](#contributing)

## Introduction
The simulation of our robot (hexapod) is made in the Gazebo Harmonic environment, which we communicate with the ROS2 Jazzy Jalisco framework. Everyone working on the simulation is advised to familiarize themselves with the documentation provided below.

## Requirements
In order to start working with a simulation it is neccesary to install things listed below:
1. Ubuntu 24.04 (recommended, but other Ubuntu 24 release should also work).  
[Link to example tutorial, how to install Ubuntu with dual boot](https://www.youtube.com/watch?v=mXyN1aJYefc&ab_channel=Robtech)
2. ROS2 Jazzy Jalisco.  
[Link to ROS2 Jazzy installation tutorial](https://docs.ros.org/en/jazzy/Installation.html)
3. Gazebo Harmonic.  
[Link to Gazebo Harmonic installation tutorial](https://gazebosim.org/docs/harmonic/install/)
4. MoveIT IS NOT NECESSARY

## Building with real robot
The goal of that folder is to connect real robot controllers and simulation. Everything works the same as in other parts of system - go to folder ros2_ws_hex, run 
` colcon build `
then ` source install/setup.bash `, then u can use codes that we were using before `ros2 launch hex_gz gazebo.launch.py ` (as described in the next part)


OR 

u can launch simualtion using ` mode ` parameter in `main.launch.py` then u should run `ros2 launch hex_gz main.launch.py mode:={sim/real}` choose sim if u want to run only gazebo simulation (it simply runs gazebo.launch.py code) or if u want to test smth on real robot use `real` parameter. Simulation would also run in that case, as we want to use it to see how our robot is doing. That would also launch serwer and other terminals that are needed for testing the hexapod in real world.

## Building Packages
This section will show you how to build ros2 packages of our project.  

*After installing ROS2 and gazebo according to tutorials linked above you should have ROS2 sourced in every terminal, but when some strange "files not found" error occcurs, make sure that ROS2 is sourced properly.*

1. Firstly clone the repository of the Hexapod project in directory of your choice.
~~~
cd YourDir
git clone https://github.com/Siedmiu/Hexapod.git
~~~  
2. Then, go to the proper ROS2 workspace (it is possible that we currently have few workspaces saved, make sure you go to the right one).
~~~
cd Hexapod/simulation/ros2_ws_hex
~~~  
3. Build packages, you need to do it everytime you make any changes to the code or if you have just cloned the repository. This may take few seconds to complete. You don't need to delete existing build files if you make any changes to the code, the changes will overwrite automatically. Deleting build files will make colcon to build packages again, which takes more time.
~~~
colcon build
~~~ 
4. Source builded packages, so the ROS2 could know where to look for the files.
~~~
source install/setup.bash
~~~


## Usage after building
This section will explain how to launch executables from packages.

In ROS we have 2 types of "executables" we can launch:
### Launch files (usually ending with .launch.py).  
Syntax for launching those files:  
~~~
ros2 launch [name of the package] [full name of the launch file]
~~~
for example if we want to launch our gazebo simulation:
~~~
ros2 launch hex_gz gazebo.launch.py
~~~

### "Scripts" (files with .py/.cpp/c extensions)
Syntax for launching those files:  
~~~
ros2 run [name of the package] [full name of the launch file]
~~~
for example if we want to launch our script for moving robot leg:
~~~
ros2 run hex_gz one_leg.py
~~~


## Contributing
This section is dedicated for those who will work with the ROS or/and gazebo. In this section I would like to briefly explain what's happening in this file structure (or at least as much as I know).
### Intro
You need to remember that our simulation structure comes from open source [Open manipulator project](https://github.com/ROBOTIS-GIT/open_manipulator), which also uses ROS to control real robot. For us, this means that some files or parts of the code is commited to control real robot and is unnecessary for the simulation, though I decided to leave those parts in case we would like to control real hexapod via ROS framework.

Also in case you really don't know what to do, you always can just take open_manipulator project as example

We are using "open_manipulator_x" version of their robot.

### Generally about packages
Every ROS package has 2 files **CMakeLists.txt** and **package.xml** which describes how the package should be built. Everytime you change name of the folder, package or script or crate new folder inside of the package or new script you need to make sure that those two files know about it (usually only CMakeLists.txt).  
#### Here's part of the CMakeLists file from hex_gz package:

~~~
install(DIRECTORY launch config worlds
  DESTINATION share/${PROJECT_NAME}
)

install(FILES open-manipulator-x-cdc.rules
  DESTINATION share/${PROJECT_NAME}
)

install(PROGRAMS scripts/x_create_udev_rules
  scripts/init_position_for_x.py
  scripts/one_leg.py
  DESTINATION lib/${PROJECT_NAME}
)
~~~
If you add new file, directory or script directly in the package directory, you need to add it in corresponding sections of the CMakeLists.

#### Here's part of the package.xml file from hex_gz package:

~~~
  <depend>ros_gz_bridge</depend>
  <depend>ros_gz_sim</depend>
  <depend>ros_gz_image</depend>
  <exec_depend>robot_state_publisher</exec_depend>
  <exec_depend>gz_ros2_control</exec_depend>
  <exec_depend>ros2_control</exec_depend>
  <exec_depend>ros2_controllers</exec_depend>
  <exec_depend>gripper_controllers</exec_depend>
  <exec_depend>rviz2</exec_depend>
  <exec_depend>hexapod_description</exec_depend>
  <exec_depend>xacro</exec_depend>
~~~
If you use some new dependency which was not yet used in this package, you need to add it here.

#### Building packages
Every package of the project is build by colcon build separetely and if colcon finds error in the package, this one particular package won't be built, but other packages could be built, it is good to carefully read error logs in terminal, because 50% errors are those connected with wrond filde/directory name.
Although it shouldn't make any errors it is highly reccomended to put files in their corresponding directories to keep the package structure in order. So .xacro, .urdf files go to "urdf" directory, .launch.py files goes to "launch" directory, .py programs goes to "scripts" directory etc.

### Purpose of packages
General purpose of having multiple packages is to remain order. I would like to briefly explain the purpose of packages in our project.
#### "hexapod" package
It is main package, but the smallest one, it generally describes the simulation project. You should change its CMakeLists when you add new package to the simulation project. You shouldn't add any scripts, launches or urdf/xacro to this package.
#### "hexapod_description" package
This package describes how the robot is built in the simulation. There are xacro/urdf that descibes position, rotation and name of every link of our robot. In those files we put all of the inertia or sensor data aswell. In this package there are also every mesh used in simulation.  
You shouldn't put any important launch files or scripts here.
**hexapod.gazebo.xacro** - is used by the main xacro file, I am not sure whether it is important for the simulation or only to harware for now  
**model_x.launch.py** - unused  
**hexapod_system.ros2_control.xacro** - only 4 lines are important for simulation and for the simulation purposes it shouldn't be changed  
**hexapod.rviz** - configuration file for ROS Rviz GUI (tool to visualise our robot)  
**hexapod.urdf.xacro** - main xacro file, directly used during launching the simulation, it loads other xacro files  
**hexapod_leg.urdf.xacro** - file that contains all of the links and joints  

#### "hex_gz" package
In this package we put all the important launch files or scripts. Short name is helpful during typing "run" commands in console.  
**gazebo_controller_manager.yaml** - this file contains configuration for gazebo controller. You can change some settings of the controllers moving joints in simulation. Might be important for people that implement new walking algorythms.  
**hardware_controller_manager.yaml** - has configuration for real robot controller, not important for the simulation.  
**gazebo.launch.py** - Main launch file of the simulation.  
**hardware_x.launch.py** - Launch fie for real robot. Unadapted to hexapod settings, currently unsused.  
**ai_teleoperation** - launch file to start the gazebo simulator with the possibility to move joints via keyboard. Unadapted to hexapod settings, currently unused.  
**one_leg.py** - script that can succesfully move one of the hexapod legs, should be example for implementing further algorythms.  
**x_create_udev_rules** - unused, may be usued to control real robot  
**empty_world.sdf** - contains an SDF description of the world surrounding hexapod, currently empty world.

#### "ros2_control" package
This package contains unchanged controllers for ROS2 (not sure what they're doing).
