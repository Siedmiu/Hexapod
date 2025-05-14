### Updates from hackathon 14.05
- added imu module

- started implementing interface to controll robot movements from app (currently )

- found problem - cannot colcon build files in `Project/ros2_ws/src/pajak/pajak `


- file in `Test/src/run_all.sh` - run from one console simulation and server terminal, u can add there more bash scripts, to open more different terminals from one place

`chmod +x run_all.sh `

` ./run_all.sh ESP_IP `

change ESP_IP to your ESP_IP!!!

TODO:
- configure imu, connect imu topic and get data from real robot, send them to the simulation
- redefine all those connections between files and make more transparent structure (e.g. `pajak/pajak -> pajak `)