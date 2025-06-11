# utils/hand_processor.py
import cv2
import mediapipe as mp

def process_hand_image(image_path):
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(static_image_mode=True, max_num_hands=1, min_detection_confidence=0.5)
    mp_drawing = mp.solutions.drawing_utils

    image = cv2.imread(image_path)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hands.process(image_rgb)

    if not results.hand_landmarks:
        print("No se detectó ninguna mano.")
        return

    for hand_landmarks in results.hand_landmarks:
        for idx, landmark in enumerate(hand_landmarks.landmark):
            print(f"Punto {idx}: x={landmark.x}, y={landmark.y}, z={landmark.z}")
