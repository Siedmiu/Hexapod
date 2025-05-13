import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/milosz/Dokumenty/Main/Hexapod/PlatformIO/Projects/ros2_ws/install/pajak'
