import cv2
import mediapipe as mp
import pygame # Its a lib for sound generation for games
import numpy as np

# Initializing the mixer for audio production
pygame.mixer.pre_init(44100, -16, 2)
pygame.init()

SAMPLE_RATE = 44100 # Defalut sample rate for audio

# Function to generate a tone using a sine wave
def generate_tone(freq, duration=2.0): # we are setting the duration to 2 sec for now. But we'll loop it infinitely in a loop
    sample_rate = 44100
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)

    # Creating sine wave using the numpy sine function
    wave = np.sin(2 * np.pi * freq * t)

    # Converting to 16-bit signed integers
    audio = (wave * 32767).astype(np.int16)

    # Now this was a mono audio (means that it has onyl one channel). But we need to convert it into stereo (2 channels) for usage in pygame to produce sound

    # Convert mono → stereo
    stereo_audio = np.column_stack((audio, audio))  # We are just stacking the 2 mono audios to form a stereo audio

    return pygame.sndarray.make_sound(stereo_audio) # Returning the sound produced using the pygame 


# Frequencies for corresponding notes
NOTES = {
    "C5": 523.25, "D5": 587.33, "E5": 659.25,
    "F5": 698.46, "G5": 783.99, "A5": 880.00,
    "B5": 987.77, "C6": 1046.50, "D6": 1174.66, "E6": 1318.51
}

# Synth sounds: Dictionary for storing the synth sounds generated using the generate_tone function for each corresponding note in NOTES Dict
synth_sounds = {k: generate_tone(v) for k, v in NOTES.items()}

# Piano samples: Also loading the piano samples for each note in NOTES Dict
piano_sounds = {
    k: pygame.mixer.Sound(f"Sounds/Piano/{k}.wav") for k in NOTES
}

# Setting up Mediapipe and drawing utilities
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

# Assigning notes to each finger of both hands
LEFT_HAND = ["C5", "D5", "E5", "F5", "G5"]
RIGHT_HAND = ["A5", "B5", "C6", "D6", "E6"]

# Assiging the values of the finger_tips as in the mediapipe lib
finger_tips = [4, 8, 12, 16, 20]

# Assigning the values of the finger_mcps (base/knuckles) as in the mediapipe lib
finger_mcps = [1, 5, 9, 13, 17]

active_notes = {}
MODE = "PIANO"

# This is the input recieving loop
cap = cv2.VideoCapture(0)

# This recieves the hand landmarks using mediapipe
with mp_hands.Hands(
    max_num_hands=2,
    min_detection_confidence=0.6,
    min_tracking_confidence=0.6
) as hands:

    # Main loop as long as the camera is open
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)  # We need to flip the frame for avoiding mirror images
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) # COnverting the frame from BGR to RGB as mediapipe works on RGB images
        results = hands.process(rgb) # This processes the RGB frame and gives us the hand landmarks if any hand is detected

        # This is the loop for any hand landmarks detected
        if results.multi_hand_landmarks:
            for h, hand in enumerate(results.multi_hand_landmarks): # Looping through each hand detected using enumerate to get the index of the hand as well

                mp_draw.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS) # Drawing the hand landmarks on the frame

                # for loop for all 5 fingers of each hand
                for i in range(5):
                    tip = finger_tips[i] # Getting the tip landmark index of the finger
                    mcp = finger_mcps[i] # Getting the mcp (base/knuckle) landmark index of the finger

                    finger_down = hand.landmark[tip].y > hand.landmark[mcp].y # Defining the condition for the finger is down or not
                    note = LEFT_HAND[4 - i] if h == 0 else RIGHT_HAND[i]

                    # If finger is down, then the note is played accordingly based on the mode selected
                    if finger_down:
                        if note not in active_notes:
                            if MODE == "PIANO":
                                active_notes[note] = piano_sounds[note].play()
                            else:
                                active_notes[note] = synth_sounds[note].play()
                    else:
                        if note in active_notes:
                            active_notes[note].stop()
                            del active_notes[note]

        # Mode switching
        key = cv2.waitKey(1) & 0xFF
        if key == ord('p'):
            MODE = "PIANO"
            print("Mode: PIANO")
        elif key == ord('s'):
            MODE = "SYNTH"
            print("Mode: SYNTH")
        elif key == 27:
            break

        cv2.imshow("AirTune", frame)

cap.release() # Releases all the resources and the camera
cv2.destroyAllWindows() # Closes the window