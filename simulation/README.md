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
