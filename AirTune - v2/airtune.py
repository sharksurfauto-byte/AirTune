# --- 1. Imports ---
import cv2
import mediapipe as mp
import pygame # Library for real-time audio generation and playback
import numpy as np
from trumpet import VirtualTrumpet # Custom module for Trumpet instrument logic

# --- 2. Audio Initialization ---
# Pre-init mixer to 44.1kHz, 16-bit, stereo with reasonable buffer
pygame.mixer.pre_init(44100, -16, 2)
pygame.init()

SAMPLE_RATE = 44100 

# --- 3. Sound Generation Helper ---
def generate_tone(freq, duration=2.0):
    """
    Generates a sine wave tone for a specific frequency.
    Returns: a pygame Sound object.
    """
    sample_rate = 44100
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)

    # Creating sine wave
    wave = np.sin(2 * np.pi * freq * t)

    # Converting to 16-bit signed integers (PCM format)
    audio = (wave * 32767).astype(np.int16)

    # Convert Mono -> Stereo (stack columns)
    stereo_audio = np.column_stack((audio, audio)) 

    return pygame.sndarray.make_sound(stereo_audio)


# --- 4. Notes & Synthesis ---
# Frequencies for keys
NOTES = {
    "C5": 523.25, "D5": 587.33, "E5": 659.25,
    "F5": 698.46, "G5": 783.99, "A5": 880.00,
    "B5": 987.77, "C6": 1046.50, "D6": 1174.66, "E6": 1318.51
}

# Pre-generate Synth Sounds (Sine Waves)
synth_sounds = {k: generate_tone(v) for k, v in NOTES.items()}

# Load Piano Sounds (WAV Files)
piano_sounds = {
    k: pygame.mixer.Sound(f"Sounds/Piano/{k}.wav") for k in NOTES
}

# --- 5. MediaPipe Setup ---
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

# --- 6. Hand Mapping & Game State ---

# Notes assigned to each finger [thumb, index, middle, ring, pinky]
LEFT_HAND = ["G5", "F5", "E5", "D5", "C5"]
RIGHT_HAND = ["A5", "B5", "C6", "D6", "E6"]

# Landmark Indices
finger_tips = [4, 8, 12, 16, 20] # Thumb to Pinky Tips
finger_pips = [2, 6, 10, 14, 18]  # Thumb to Pinky Middle Joints (PIP)

active_notes = {} # Tracks currently playing notes in Piano/Synth mode
MODE = "PIANO"    # Start in Piano mode
trumpet = VirtualTrumpet() # Initialize Trumpet instrument

# Chord Library for Detection
CHORD_LIBRARY = {
    "C Major": {"C5", "E5", "G5"},
    "D Minor": {"D5", "F5", "A5"},
    "E Minor": {"E5", "G5", "B5"},
    "F Major": {"F5", "A5", "C6"},
    "G Major": {"G5", "B5", "D6"},
    "A Minor": {"A5", "C6", "E6"},
}

# --- 7. Main Application Loop ---
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

        frame = cv2.flip(frame, 1)  # Mirror view
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) # Required for MediaPipe
        results = hands.process(rgb)

        note_coords = {} # Stores on-screen coords of active notes for visual effects 
        
        # --- LOGIC BRANCH: TRUMPET VS PIANO/SYNTH ---
        
        # Branch A: Trumpet Mode (Monophonic, Valves + Breath)
        if MODE == "TRUMPET":
             # Draw hand landmarks
             if results.multi_hand_landmarks:
                 for hand_landmarks in results.multi_hand_landmarks:
                     mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
             
             trumpet.process_hands(results)
             trumpet.update()
             # trumpet.draw(frame) # UI disabled
        
        # Branch B: Piano/Synth Mode (Polyphonic, Finger Tapping)
        elif results.multi_hand_landmarks:
            for h, hand in enumerate(results.multi_hand_landmarks): 

                mp_draw.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS) 

                # Check all 5 fingers
                for i in range(5):
                    tip = finger_tips[i] 
                    pip = finger_pips[i] 

                    # Special handling for THUMB (index 0) - checks horizontal movement
                    if i == 0:
                        # Thumb folds horizontally toward palm
                        # Right hand (h=0): thumb moves right when folded
                        # Left hand (h=1): thumb moves left when folded
                        if h == 0:  # Left hand on screen (first detected)
                            finger_down = hand.landmark[tip].x < hand.landmark[pip].x
                        else:  # Right hand on screen
                            finger_down = hand.landmark[tip].x > hand.landmark[pip].x
                    else:
                        # Other fingers: use vertical detection (Tip below Middle Joint)
                        finger_down = hand.landmark[tip].y > hand.landmark[pip].y 
                    
                    note = LEFT_HAND[i] if h == 0 else RIGHT_HAND[i]

                    # Visual Effect Coordinate storage
                    h_img, w_img, _ = frame.shape
                    note_coords[note] = (int(hand.landmark[tip].x * w_img), int(hand.landmark[tip].y * h_img))

                    # Sound Triggering
                    if finger_down:
                        if note not in active_notes:
                            if MODE == "PIANO":
                                active_notes[note] = piano_sounds[note].play()
                            else:
                                active_notes[note] = synth_sounds[note].play(loops=-1) # Infinite loop for synth
                    else:
                        if note in active_notes:
                            active_notes[note].stop()
                            del active_notes[note]

        # --- 8. Input Handling ---
        key = cv2.waitKey(1) & 0xFF
        if key == ord('p'):
            MODE = "PIANO"
            print("Switched to: PIANO")
        elif key == ord('s'):
            MODE = "SYNTH"
            print("Switched to: SYNTH")
        elif key == ord('t'):
            MODE = "TRUMPET"
            print("Switched to: TRUMPET")
        elif key == 27: # ESC to quit
            break

        # --- 9. Visual Overlays (Chord Detection) --- [DISABLED]
        # # Detect active chord based on currently playing notes
        # current_active_set = set(active_notes.keys())
        # detected_chord = None
        # for chord_name, notes in CHORD_LIBRARY.items():
        #     if notes.issubset(current_active_set):
        #         detected_chord = chord_name
        #         break

        # # Draw Mode Label
        # cv2.putText(frame, f"MODE: {MODE}", (10, 30), 
        #             cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        # 
        # # Draw Chord Name & Neon Lines
        # if detected_chord:
        #     # Background Box
        #     cv2.rectangle(frame, (10, 50), (250, 95), (0, 0, 0), -1)
        #     cv2.putText(frame, f"CHORD: {detected_chord}", (20, 85), 
        #                 cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
        #     
        #     # Neon Lines Effect
        #     chord_notes = list(CHORD_LIBRARY[detected_chord])
        #     for i in range(len(chord_notes)):
        #         for j in range(i + 1, len(chord_notes)): 
        #             n1, n2 = chord_notes[i], chord_notes[j]
        #             if n1 in note_coords and n2 in note_coords: 
        #                 p1, p2 = note_coords[n1], note_coords[n2]
        #                 # Glow Effect (Thick Dark Green + Thin Bright Green)
        #                 cv2.line(frame, p1, p2, (0, 150, 0), 5) 
        #                 cv2.line(frame, p1, p2, (0, 255, 0), 2) 

        cv2.imshow("AirTune", frame)

cap.release()
cv2.destroyAllWindows()
pygame.quit()
