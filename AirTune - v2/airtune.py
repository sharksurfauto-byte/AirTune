import cv2
import mediapipe as mp
import pygame
import time
import os

# ---------------- SETUP ----------------
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

pygame.mixer.init()

# Sound folder
SOUND_DIR = os.path.join("Sounds", "Piano")

# Load sounds
notes = {
    "C5": pygame.mixer.Sound(os.path.join(SOUND_DIR, "C5.wav")),
    "D5": pygame.mixer.Sound(os.path.join(SOUND_DIR, "D5.wav")),
    "E5": pygame.mixer.Sound(os.path.join(SOUND_DIR, "E5.wav")),
    "F5": pygame.mixer.Sound(os.path.join(SOUND_DIR, "F5.wav")),
    "G5": pygame.mixer.Sound(os.path.join(SOUND_DIR, "G5.wav")),
    "A5": pygame.mixer.Sound(os.path.join(SOUND_DIR, "A5.wav")),
    "B5": pygame.mixer.Sound(os.path.join(SOUND_DIR, "B5.wav")),
    "C6": pygame.mixer.Sound(os.path.join(SOUND_DIR, "C6.wav")),
    "D6": pygame.mixer.Sound(os.path.join(SOUND_DIR, "D6.wav")),
    "E6": pygame.mixer.Sound(os.path.join(SOUND_DIR, "E6.wav")),
}

# Hand → Note mapping
LEFT_HAND = ["C5", "D5", "E5", "F5", "G5"]
RIGHT_HAND = ["A5", "B5", "C6", "D6", "E6"]

# Finger landmarks
finger_tips = [4, 8, 12, 16, 20]
finger_mcps = [1, 5, 9, 13, 17]

# State tracking
finger_state = [False] * 10
active_notes = {}
COOLDOWN = 0.15

# ---------------- MAIN LOOP ----------------
cap = cv2.VideoCapture(0)

with mp_hands.Hands(
    max_num_hands=2,
    min_detection_confidence=0.6,
    min_tracking_confidence=0.6
) as hands:

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)

        if results.multi_hand_landmarks:
            for h, hand in enumerate(results.multi_hand_landmarks):

                mp_draw.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)

                for i in range(5):
                    finger_index = h * 5 + i
                    tip = finger_tips[i]
                    mcp = finger_mcps[i]

                    finger_down = hand.landmark[tip].y > hand.landmark[mcp].y

                    # Determine note
                    if h == 0:
                        note = LEFT_HAND[4 - i]
                    else:
                        note = RIGHT_HAND[i]

                    if finger_down:
                        if not finger_state[finger_index]:
                            if note not in active_notes:
                                ch = notes[note].play(-1)  # sustain
                                active_notes[note] = ch
                            finger_state[finger_index] = True

                        # Draw note name
                        x = int(hand.landmark[tip].x * frame.shape[1])
                        y = int(hand.landmark[tip].y * frame.shape[0])
                        cv2.putText(frame, note, (x, y - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                                    (0, 255, 0), 2)
                    else:
                        if finger_state[finger_index]:
                            if note in active_notes:
                                active_notes[note].stop()
                                del active_notes[note]
                            finger_state[finger_index] = False

        cv2.imshow("AirTune - Gesture Piano", frame)

        if cv2.waitKey(1) & 0xFF == 27:
            break

cap.release()
cv2.destroyAllWindows()
