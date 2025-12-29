import cv2
import mediapipe as mp
import pygame
import time

class VirtualTrumpet:
    def __init__(self):
        """Initializes the VirtualTrumpet, loads sounds, and sets up state variables."""
        # --- Configuration ---
        self.SOUND_DIR = "Sounds/Trumpet"
        self.NOTES_FILES = {
            "C": "C4.wav",
            "B": "B3.wav",
            "Bb": "Bb3.wav",
            "A": "A3.wav",
            "Ab": "Ab3.wav",
            "G": "G3.wav",
            "Gb": "Gb3.wav",
            "F": "F3.wav"
        }

        # Valve to Note Mapping (Valve 1=Index, 2=Middle, 3=Ring)
        # Tuple format: (Valve1, Valve2, Valve3) -> Note Name
        # 0 = Open (Up), 1 = Pressed (Down)
        self.USER_VALVE_MAP = {
            (0, 0, 0): "C",
            (1, 0, 0): "B",
            (0, 1, 0): "Bb",
            (1, 1, 0): "A",
            (0, 0, 1): "Ab",
            (0, 1, 1): "G",
            (1, 0, 1): "Gb",
            (1, 1, 1): "F"
        }

        # Hand Landmarks
        self.MP_TIPS = [8, 12, 16]   # Index, Middle, Ring (Tips)
        self.MP_PIPS = [6, 10, 14]   # Index, Middle, Ring (Middle Joints - PIP)

        # Init Pygame Mixer if not checks
        if not pygame.mixer.get_init():
            pygame.mixer.pre_init(44100, -16, 2, 1024)
            pygame.init()
            pygame.mixer.set_num_channels(8)

        # Load Sounds
        self.sounds = {}
        try:
            for note, filename in self.NOTES_FILES.items():
                self.sounds[note] = pygame.mixer.Sound(f"{self.SOUND_DIR}/{filename}")
            print("Trumpet sounds loaded.")
        except Exception as e:
            print(f"Error loading trumpet sounds: {e}")

        # State Variables
        self.current_note_name = None
        self.is_blowing = False
        self.active_sound_channel = None
        
        # Real-time Inputs
        self.right_hand_valves = [0, 0, 0] # State of the 3 valves [0 or 1]
        self.left_hand_active = False # Blowing state (True if detected and fist closed)

    def process_hands(self, results):
        """
        Analyzes MediaPipe results to determine Valve (Right Hand) and Breath (Left Hand) states.
        
        Args:
            results: The output object from mp_hands.process(rgb_image).
        """
        # Reset per-frame state
        self.right_hand_valves = [0, 0, 0]
        self.left_hand_active = False # Default off unless detected and closed
        
        if not results.multi_hand_landmarks:
            return

        for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
            label = handedness.classification[0].label 
            
            # RIGHT HAND -> VALVES (Index, Middle, Ring Control Pitch)
            if label == "Right":
                for i in range(3):
                    tip_y = hand_landmarks.landmark[self.MP_TIPS[i]].y
                    pip_y = hand_landmarks.landmark[self.MP_PIPS[i]].y
                    # Fold Logic: If Tip Y > PIP Y (Tip is lower than middle joint), the finger is "Pressed"
                    if tip_y > pip_y:
                        self.right_hand_valves[i] = 1
                    else:
                        self.right_hand_valves[i] = 0

            # LEFT HAND -> BREATH (Fist = Blow, Open = Stop)
            if label == "Left":
                extended_count = 0
                # Check all 4 fingers (Index to Pinky)
                for tip_idx, mcp_idx in zip([8, 12, 16, 20], [5, 9, 13, 17]):
                    if hand_landmarks.landmark[tip_idx].y < hand_landmarks.landmark[mcp_idx].y:
                        extended_count += 1
                
                # Fist condition: If 2 or fewer fingers are extended, we consider it a "Fist" -> Blowing
                if extended_count <= 2: 
                    self.left_hand_active = True
                else:
                    self.left_hand_active = False

    def update(self):
        """
        Updates the audio engine based on the current state of valves and breath.
        Handles starting, stopping, and changing notes.
        """
        # Determine Target Note based on Valves
        valve_tuple = tuple(self.right_hand_valves)
        target_note_name = self.USER_VALVE_MAP.get(valve_tuple, "C") # Default to C if unknown combo
        
        should_play = self.left_hand_active
        
        if should_play:
            if not self.is_blowing:
                # Case 1: Just started blowing
                if self.active_sound_channel: self.active_sound_channel.stop()
                if target_note_name in self.sounds:
                    self.active_sound_channel = self.sounds[target_note_name].play(loops=-1)
                self.current_note_name = target_note_name
                self.is_blowing = True
            else:
                # Case 2: Already blowing, check if note changed (Legato)
                if target_note_name != self.current_note_name:
                    if self.active_sound_channel: self.active_sound_channel.stop()
                    if target_note_name in self.sounds:
                        self.active_sound_channel = self.sounds[target_note_name].play(loops=-1)
                    self.current_note_name = target_note_name
        else:
            if self.is_blowing:
                # Case 3: Stopped blowing
                if self.active_sound_channel: self.active_sound_channel.stop()
                self.is_blowing = False
                self.current_note_name = None

    def draw(self, frame):
        """
        Draws the Trumpet UI overlays onto the frame.
        
        Args:
            frame: The BGR image from OpenCV.
        """
        # Breath Status Display
        status_color = (0, 255, 0) if self.is_blowing else (0, 0, 255)
        status_text = "BLOWING" if self.is_blowing else "NO BREATH"
        # Position slightly lower to avoid collision if main app draws top left
        cv2.putText(frame, f"BREATH: {status_text}", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.8, status_color, 2)
        
        if self.is_blowing:
            cv2.putText(frame, f"NOTE: {self.current_note_name}", (10, 160), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 0), 3)

        # Draw Valve Indicators (Top Right)
        for i in range(3):
            color = (0, 0, 255) if self.right_hand_valves[i] else (200, 200, 200) # Red if pressed, Grey if open
            center = (500 + i * 40, 50)
            cv2.circle(frame, center, 15, color, -1)
            cv2.circle(frame, center, 15, (0, 0, 0), 2)
            # Label valves 1, 2, 3
            cv2.putText(frame, str(i+1), (center[0]-5, center[1]+5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

# Main block for testing
if __name__ == "__main__":
    cap = cv2.VideoCapture(0)
    trumpet = VirtualTrumpet()
    
    mp_hands = mp.solutions.hands
    mp_draw = mp.solutions.drawing_utils
    
    with mp_hands.Hands(max_num_hands=2) as hands:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: break
            
            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb)
            
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            trumpet.process_hands(results)
            trumpet.update()
            trumpet.draw(frame)
            
            cv2.imshow("Trumpet Test", frame)
            if cv2.waitKey(1) & 0xFF == 27: break
    
    cap.release()
    cv2.destroyAllWindows()
