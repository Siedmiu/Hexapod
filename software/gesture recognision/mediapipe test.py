import cv2
import mediapipe as mp
import math


class HandGestureDetector:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils
        self.cap = cv2.VideoCapture(0)
        self.last_gesture = None
        self.last_position = (0, 0)
        self.show_preview_window = True

    def calculate_distance(self, p1, p2):
        return math.sqrt((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2)

    def detect_gesture(self, screen_width, screen_height):
        success, image = self.cap.read()
        if not success:
            return False, None, self.last_position

        image = cv2.flip(image, 1)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.hands.process(image_rgb)
        image_height, image_width, _ = image.shape

        gesture = None
        position = self.last_position  # Default to last known position

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                wrist = hand_landmarks.landmark[self.mp_hands.HandLandmark.WRIST]
                x = int(wrist.x * screen_width)
                y = int(wrist.y * screen_height)
                position = (x, y)

                # landmarks for gesture detection
                #finger landmarks
                thumb_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.THUMB_TIP]
                index_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]
                index_pip = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_PIP]
                middle_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
                middle_pip = hand_landmarks.landmark[self.mp_hands.HandLandmark.MIDDLE_FINGER_PIP]
                ring_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.RING_FINGER_TIP]
                ring_pip = hand_landmarks.landmark[self.mp_hands.HandLandmark.RING_FINGER_PIP]
                pinky_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.PINKY_TIP]
                pinky_pip = hand_landmarks.landmark[self.mp_hands.HandLandmark.PINKY_PIP]
                thumb_ip = hand_landmarks.landmark[self.mp_hands.HandLandmark.THUMB_IP]
                thumb_mcp = hand_landmarks.landmark[self.mp_hands.HandLandmark.THUMB_MCP]
                #bounding box landmark
                xs = [landmark.x for landmark in hand_landmarks.landmark]
                ys = [landmark.y for landmark in hand_landmarks.landmark]
                x_range = max(xs) - min(xs)
                y_range = max(ys) - min(ys)

                #if hand is at a weird position and points overlap, it will be considered as invalid
                min_range_threshold = 0.05
                aspect_ratio = x_range / y_range if y_range != 0 else float('inf')
                valid_hand_pose = x_range > min_range_threshold and y_range > min_range_threshold and aspect_ratio < 3.0

                #finger shape logic
                index_extended = index_tip.y < index_pip.y
                middle_closed = middle_tip.y > middle_pip.y
                ring_closed = ring_tip.y > ring_pip.y
                pinky_closed = pinky_tip.y > pinky_pip.y
                thumb_up = thumb_tip.y < thumb_ip.y < thumb_mcp.y
                index_closed = index_tip.y > index_pip.y

                #okay loop
                thumb_index_distance = self.calculate_distance(thumb_tip, index_tip)
                is_okay_circle = thumb_index_distance < 0.08

                #highest_finger
                finger_tips = {
                    "thumb": thumb_tip.y,
                    "index": index_tip.y,
                    "middle": middle_tip.y,
                    "ring": ring_tip.y,
                    "pinky": pinky_tip.y
                }
                highest_finger = min(finger_tips, key=finger_tips.get)

                #gesture logic
                if valid_hand_pose:
                    if thumb_up and index_closed and middle_closed and ring_closed and pinky_closed and highest_finger == "thumb":
                        gesture = "thumbs_up"

                    elif index_extended and middle_closed and pinky_closed and highest_finger == "index" and not is_okay_circle:
                        gesture = "index_up"

                    elif is_okay_circle and not middle_closed and not ring_closed and not pinky_closed:
                        gesture = "okay"

                if self.show_preview_window:
                    self.mp_drawing.draw_landmarks(image, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)

        if self.show_preview_window:
            if gesture:
                cv2.putText(image, f"Gesture: {gesture}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            #cv2.putText(image, f"Cursor: ({position[0]}, {position[1]})", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(255, 0, 0), 1)
            cv2.imshow('Hand Gesture Control', image)
            cv2.waitKey(1)

        self.last_position = position
        self.last_gesture = gesture

        return True, gesture, position

    def toggle_preview(self):
        self.show_preview_window = not self.show_preview_window
        if not self.show_preview_window:
            cv2.destroyAllWindows()

    def close(self):
        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    detector = HandGestureDetector()
    screen_width = 1280
    screen_height = 720

    try:
        while True:
            detected, gesture, position = detector.detect_gesture(screen_width, screen_height)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        detector.close()