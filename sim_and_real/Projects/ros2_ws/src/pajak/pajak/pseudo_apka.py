#!/usr/bin/env python3
import rospy
from std_msgs.msg import String

def main():
    rospy.init_node('pseudo_apka', anonymous=True)
    pub = rospy.Publisher('/robot/command', String, queue_size=10)
    rospy.sleep(1)  # Czekamy na inicjalizację publishera

    print("Witaj w pseudo-apce robota! Wpisz komendę:")
    print("Dostępne: move_forward, move_backward, turn_left, turn_right, stop, exit")

    while not rospy.is_shutdown():
        cmd = input(">>> ").strip()

        if cmd == "exit":
            print("Zamykam apkę...")
            break

        pub.publish(cmd)
        print(f"[INFO] Wysłano komendę: {cmd}")

if __name__ == '__main__':
    try:
        main()
    except rospy.ROSInterruptException:
        pass
