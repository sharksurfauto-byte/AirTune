import cv2
import mediapipe as mp
import pygame

mp_hands = mp.solutions.hands
mp_drawings = mp.solutions.drawing_utils

pygame.mixer.init()

# Creating a list of sounds:

sounds = [
    pygame.mixer.Sound("#fa.WAV"),
    pygame.mixer.Sound("la.WAV"),
    pygame.mixer.Sound("re.WAV"),
    pygame.mixer.Sound("#do.WAV"),
    pygame.mixer.Sound("#sol.WAV"),
    pygame.mixer.Sound("si.WAV")
]

# Function to check if finger is down:

def is_finger_down(landmarks, finger_tip, finger_mcp):
  return landmarks[finger_tip].y > landmarks[finger_mcp].y

cap = cv2.VideoCapture(0)

with mp_hands.Hands(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5,
    max_num_hands=2
) as hands:
    
    finger_state = [False] * 6  # To track the state of each finger sound

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        results = hands.process(rgb_frame)

        if results.multi_hand_landmarks:
            for h, hand_landmarks in enumerate(results.multi_hand_landmarks):
                mp_drawings.draw_landmarks(
                    frame,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS
                )

                finger_tips = [8, 12, 16, 20, 4]
                finger_mcp = [5, 9, 13, 17, 1]

                for i in range(3):
                    finger_index = i + h*3

                    if is_finger_down(hand_landmarks.landmark, finger_tips[i],  finger_mcp[i]):
                        if finger_state[finger_index] == False:
                            sounds[finger_index].play()
                            finger_state[finger_index] = True
                    else:
                        finger_state[finger_index]=False





        # 👇 ALWAYS show the frame
        cv2.imshow("AirTune", frame)

        if cv2.waitKey(1) & 0xFF == 27:  # ESC
            break

cap.release()
cv2.destroyAllWindows()
