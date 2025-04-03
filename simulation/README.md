Commit z dnia 22.03:

Udało mi się znaleźć tutorial, który faktycznie dobrze działa z naszą wersją ROSa:
https://robotlabs.gitbook.io/docs/ros/ros2-jazzy

Szczegółowa instrukcja, przygotowania środowiska znajduje się w powyższym tutorialu. Generalnie, aby zbudować pliki, należy użyć komendy:
colcon build
ros2 launch urdf_tutorial display.launch.py model:=pełna ścieżka do pliku hexapod.xacro (/ros2_ws/src/hexapod/hexapod_description/urdf/hexapod/hexapod.xacro)

po pierwszym zbudowaniu (colcon build), należy wpisać również: 
cd ~/ros2_ws
source ~/.bashrc (<- ta komenda nie koniecznie będzie działać, lepiej dać source install/setup.bash)

Należy dodać pozostałe linki i jointy. W każdym xacro następnych linków, o poprawnym położeniu danego linka decyduje pozycja jego jointa (tag origin). Nie należy zmieniać wartości w tagu origin dla linków samych w sobie. Możliwe że będzie konieczne dokładne położenie dla plików stl origin dokładnie w środku jointa.
Należy również zintegrować z wtyczką MoveIt.

----------------------Commit z dnia 22.03-------------------
Dodałem kod z tutoriala napisany w cpp, który umożliwia wpływanie na ROS, co widać w narzędziu Rviz (do wizualizacji ruchu robota). 

Instrukcja używania katalogu ros2_ws:

WYMAGANIA:
- Ubuntu 24.04.xx (xx jakakolwiek wersja)
- ROS2 Jazzy Jalisco
- MoveIt2

sposób odpalenia:
1. Odpalamy bash i przechodzimy do katalogu ros2_ws
2. Będąc w tym katalogu, wpisujemy
colcon build
3. Jak się zbuduje (pierwszy raz może to trochę potrwać), wpisujemy:
source /opt/ros/jazzy/setup.bash
source ~/ws_moveit/install/setup.bash
source install/setup.bash

gdzie ws_moveit to katalog utworzony na podstawie tutoriala:
https://moveit.picknik.ai/main/doc/tutorials/getting_started/getting_started.html
4. W jednym terminalu wpisujemy:
 ros2 launch hexapod_moveit_config demo.launch.py

to powinno odpalić Rviz z widocznym modelem robota (na razie linki). Następnie w osobnym terminalu, sourcujemy jak wcześniej odpowiednie pakiety i wpisujemy:
ros2 run hexapod_control hexapod_joint_control

to powinno poruszyć naszym jedynym jointem do zadanego kąta
