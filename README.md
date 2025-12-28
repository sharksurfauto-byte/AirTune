🎹 AirTune – Gesture-Controlled Virtual Synthesizer

AirTune is a real-time, gesture-controlled virtual musical instrument built using Computer Vision and Digital Sound Synthesis.
It allows users to play musical notes in the air using hand gestures, without touching any physical keys or controllers.

The system uses a webcam to track hand movements and converts finger gestures into musical notes in real time, functioning like a virtual piano/synthesizer.

✨ Key Features

🎥 Real-time hand tracking using MediaPipe

🎶 Synth-based sound generation (no audio samples required)

🎹 Two-hand support with independent note mapping

🔄 Live mode switching (Piano / Synth)

🎧 Sustained notes while fingers are held down

🧠 Gesture-based interaction — no keyboard or mouse needed

⚡ Real-time performance with low latency

🧠 How It Works

Hand Detection
Uses MediaPipe to detect 21 landmarks on each hand in real time.

Gesture Interpretation
Each finger is mapped to a musical note.
A note is triggered when the finger bends downward.

Sound Generation

Synth mode: Generates sine waves in real time using NumPy

Piano mode: Plays pre-recorded piano samples

Live Audio Engine
Audio is generated and controlled using pygame.mixer, allowing continuous sustain while a finger is held.

Visual Feedback
Hand landmarks and note positions are rendered live on the camera feed.

🎹 Controls
Action	Control
Play notes	Raise/lower fingers
Switch to Piano	Press P
Switch to Synth	Press S
Exit	ESC
🧩 Technologies Used

Python

OpenCV – Real-time video processing

MediaPipe – Hand landmark detection

Pygame – Audio synthesis & playback

NumPy – Signal generation

🚀 Features Implemented

Real-time gesture recognition

Polyphonic audio output

Custom sine-wave synthesizer

Sample-based piano mode

Hand-based note mapping

Stable real-time performance

🔮 Future Enhancements

Velocity-sensitive dynamics

ADSR envelope control

MIDI export

Visual piano UI

Chord recognition

Effects (reverb, delay, filters)

🧠 Why This Project Matters

This project combines computer vision, digital signal processing, and human–computer interaction into one system. It demonstrates real-world applications of AI and signal processing in creative technology.
