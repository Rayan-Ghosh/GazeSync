# Gaze & Voice Accessibility Suite
#
# This script provides hands-free computer control using head movements and voice commands.
# It's designed to assist users with motor disabilities by enabling web navigation
# (scrolling, zooming) through intuitive actions.
#
# The application operates in two modes:
# 1. Voice-Only: Responds to verbal commands for scrolling and zooming.
# 2. Voice + Face Tracking: Combines voice commands with head-gaze tracking for scrolling.
#
# Author: Rayan-Ghosh
# Version: 1.0

import cv2
import mediapipe as mp
import time
import numpy as np
import threading
from vosk import Model, KaldiRecognizer
import pyaudio
import json
import pyautogui

# --- Configuration & Global State ---

# Ask user for the desired operational mode at startup.
print("🔧 Choose input mode:")
print("1. Voice only")
print("2. Voice + Face tracking")
mode = input("Enter 1 or 2: ").strip()

# --- Global State Variables ---
voice_only_mode = mode == "1"    # True if user selects voice-only mode.
scroll_enabled = True            # Master switch for enabling/disabling scrolling.
recalibrated = False             # Flag to track if the initial calibration is complete.
calibration_start = None         # Timestamp to manage the initial calibration delay.
recalibration_timer_start = None # Timestamp to manage automatic recalibration.

# --- Core Functionality: User Input Simulation ---

def scroll_once(direction):
    """Simulates a single scroll or key press action."""
    if direction == "up":
        pyautogui.scroll(300)
    elif direction == "down":
        pyautogui.scroll(-300)
    elif direction == "left":
        # Press the left arrow key multiple times for a more significant jump.
        for _ in range(3):
            pyautogui.press("left")
    elif direction == "right":
        # Press the right arrow key multiple times for a more significant jump.
        for _ in range(3):
            pyautogui.press("right")
    print(f"🔄 SCROLL {direction.upper()}")

def zoom_control(direction):
    """Simulates zoom-in, zoom-out, or zoom-reset browser actions."""
    if direction == "in":
        pyautogui.hotkey('ctrl', '+')
    elif direction == "out":
        pyautogui.hotkey('ctrl', '-')
    elif direction == "reset":
        pyautogui.hotkey('ctrl', '0')
    print(f"🔍 ZOOM {direction.upper()}")

# --- Voice Command Processing ---

def voice_command_listener():
    """
    Runs in a separate thread to listen for and process voice commands
    using the Vosk offline speech recognition engine.
    """
    global scroll_enabled, recalibrated, calibration_start
    
    # Initialize Vosk model and recognizer.
    # Ensure "vosk-model-small-en-us-0.15" is downloaded in the project directory.
    model = Model(model_name="vosk-model-small-en-us-0.15")
    recognizer = KaldiRecognizer(model, 16000)
    
    # Set up the microphone stream.
    mic = pyaudio.PyAudio()
    stream = mic.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8192)
    stream.start_stream()

    print("🎙️ Offline voice command listener started...")

    while True:
        data = stream.read(4096, exception_on_overflow=False)
        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            command = result.get("text", "").lower()
            
            if not command:
                continue
                
            print(f"[Voice] Heard: {command}")

            # --- Command Matching Logic ---
            # The lists contain multiple variations to catch common recognition errors.
            
            # Stop/Pause scrolling
            if any(word in command for word in ["stop", "pause","dop","top","was","cause"]):
                scroll_enabled = False
                print("🛑 Voice Command: Scrolling Stopped")
            # Start/Resume scrolling
            elif any(word in command for word in ["start", "resume","dark","star","st","stat","that","presume"]):
                scroll_enabled = True
                print("▶️ Voice Command: Scrolling Started")
            # Trigger recalibration
            elif any(word in command for word in ["situation","sitting","acqusition","position","reposition","barate","deliberately","deliberate","calibrate", "celebrate", "gallery","recallibrate","recal","call","callibrate","bread","break","brate","rate","ate","at","eat","libe","libre","lib"]):
                recalibrated = False
                calibration_start = time.time()
                print("🛠 Voice Command: Recalibration triggered")

            # --- Zoom controls ---
            
            #Zoom in
            elif any(word in command for word in ["zoom in", "soon in", "room in", "gum in", "go in", "do min", "boomin","no mean","domain","you mean","zoomin","zooming"]):
                zoom_control("in")
            #Zoom out
            elif any(word in command for word in ["zoom out", "soon out", "room out", "doom out", "go out", "boom out","zoomout"]):
                zoom_control("out")
            #Reset zoom
            elif any(word in command for word in ["reset zoom", "default zoom", "normal zoom", "zoom reset", "zoom default", "zoom normal","original","reset","default","default view","reset view","research zoom","default real","said view","research you"]):
                zoom_control("reset")

            # --- Scrolling commands (only active in voice-only mode) ---

            #Scroll up
            elif voice_only_mode and scroll_enabled:
                if any(word in command for word in ["up","cup","hub","pup","sub","hup","dup","tup","sup","zup","bup","op","pop"]):
                    scroll_once("up")
                #Scroll down
                elif any(word in command for word in ["down","drown","downry","dong","lawn","lown","don't","don","down","dowd","dome","dome","dome","dome","nown","now"]):
                    scroll_once("down")
                #Scroll left
                elif any(word in command for word in ["left", "let", "let's", "this","listen","lefty","lost","loft","less","lives","life","live"]):
                    scroll_once("left")
                #Scroll right
                elif any(word in command for word in ["right","night","plight","height","knight","light","fight","might","flight"]):
                    scroll_once("right")

# Start the voice listener thread. It will run in the background.
threading.Thread(target=voice_command_listener, daemon=True).start()

# --- Main Application Logic ---

# If in voice-only mode, run a simple loop to keep the script alive.
if voice_only_mode:
    print("🎤 Voice-only mode active. Say commands like 'up', 'down', 'start', or 'stop'.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("🛑 Voice-only mode ended.")
        exit()

# --- Face + Voice Mode Initialization ---

# Initialize MediaPipe Face Mesh.
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=False,
    max_num_faces=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.7
)

# Start video capture from the default camera.
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("❌ Error: Cannot open camera.")
    exit()

# Define landmark indices for tracking.
# These points are used to define the neutral head position.
forehead_idx = 10
chin_idx = 152
tracked_idxs_x = [forehead_idx, chin_idx, 168] # Forehead, Chin, and a central point

# --- State for Face Tracking ---
pink_boxes = {}             # Stores the calibrated bounding boxes for tracked points.
nose_positions = []         # A buffer to smooth nose coordinates for initial calibration.
recalibration_hold_time = 3 # Seconds to hold steady inside boxes to trigger recalibration.
dead_zone = 20              # Pixel margin for the calibration boxes.
scroll_delay = 0.3          # Delay between continuous scrolls.
sleep_mode = False          # Flag to check if the face is out of frame.
last_face_seen_time = time.time()
sleep_trigger_duration = 5  # Seconds of no face detection before entering sleep mode.

# State for managing continuous scroll timing.
scroll_state = {
    "left": {"start_time": None, "last_scroll_time": 0},
    "right": {"start_time": None, "last_scroll_time": 0},
    "up": {"start_time": None, "last_scroll_time": 0},
    "down": {"start_time": None, "last_scroll_time": 0}
}

print("🟡 Hold your head steady for 2 seconds to calibrate...")

def is_all_inside_boxes(lm, h, w):
    """Check if all tracked landmarks are within their calibrated 'pink boxes'."""
    for idx in tracked_idxs_x:
        px = int(lm.landmark[idx].x * w)
        py = int(lm.landmark[idx].y * h)
        left, right, top, bottom = pink_boxes[idx]
        if not (left <= px <= right and top <= py <= bottom):
            return False
    return True

# --- Main Video Processing Loop ---
while True:
    ret, frame = cap.read()
    if not ret:
        continue

    frame = cv2.flip(frame, 1) # Flip horizontally for a mirror-like view.
    h, w = frame.shape[:2]
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb_frame)
    current_time = time.time()

    if results.multi_face_landmarks:
        lm = results.multi_face_landmarks[0]
        last_face_seen_time = current_time

        if sleep_mode:
            print("👁️ Face detected. Waking up...")
            sleep_mode = False

        # Draw a bounding box around the detected face.
        xs = [int(pt.x * w) for pt in lm.landmark]
        ys = [int(pt.y * h) for pt in lm.landmark]
        cv2.rectangle(frame, (min(xs), min(ys)), (max(xs), max(ys)), (0, 255, 0), 2)

        # --- Calibration Logic ---
        if not recalibrated:
            # During initial calibration, wait for the user to hold steady.
            if calibration_start is None:
                calibration_start = time.time()
            elif time.time() - calibration_start >= 2:
                # After 2 seconds, define the 'pink boxes' around tracked points.
                for idx in tracked_idxs_x:
                    lx = int(lm.landmark[idx].x * w)
                    ly = int(lm.landmark[idx].y * h)
                    pink_boxes[idx] = (lx - dead_zone, lx + dead_zone, ly - dead_zone, ly + dead_zone)
                recalibrated = True
                calibration_start = None
                print("✅ Initial calibration complete.")
        
        # --- Post-Calibration: Gaze Tracking & Scrolling ---
        else:
            # Get current positions of tracked points.
            current_points = [(int(lm.landmark[idx].x * w), int(lm.landmark[idx].y * h)) for idx in tracked_idxs_x]
            avg_x = int(np.mean([pt[0] for pt in current_points]))
            
            # Draw the calibrated boxes and current landmark points.
            for idx, (x, y) in zip(tracked_idxs_x, current_points):
                cv2.circle(frame, (x, y), 4, (255, 0, 255), -1)
                left, right, top, bottom = pink_boxes[idx]
                cv2.rectangle(frame, (left, top), (right, bottom), (255, 0, 255), 1)

            def process_scroll(direction, condition):
                """Handles the logic for triggering and sustaining a scroll action."""
                state = scroll_state[direction]
                if not scroll_enabled:
                    return
                
                if condition:
                    # If condition is met, start the timer.
                    if state["start_time"] is None:
                        state["start_time"] = current_time
                        scroll_once(direction)
                        state["last_scroll_time"] = current_time
                    # If held for over 1 second, scroll continuously.
                    elif current_time - state["start_time"] >= 1.0 and current_time - state["last_scroll_time"] >= scroll_delay:
                        scroll_once(direction)
                        state["last_scroll_time"] = current_time
                else:
                    # Reset timer if condition is no longer met.
                    state["start_time"] = None

            # Define the overall boundaries of the calibrated head position.
            overall_left = min([pink_boxes[idx][0] for idx in tracked_idxs_x])
            overall_right = max([pink_boxes[idx][1] for idx in tracked_idxs_x])
            forehead_y = int(lm.landmark[forehead_idx].y * h)
            chin_y = int(lm.landmark[chin_idx].y * h)
            forehead_top = pink_boxes[forehead_idx][2]
            chin_bottom = pink_boxes[chin_idx][3]

            # Check head position against boundaries to trigger scrolling.
            process_scroll("left", avg_x < overall_left)
            process_scroll("right", avg_x > overall_right)
            process_scroll("up", forehead_y < forehead_top)
            process_scroll("down", chin_y > chin_bottom)

            # --- Automatic Recalibration Logic ---
            if is_all_inside_boxes(lm, h, w):
                # If the user holds their head in the neutral position, start a timer.
                if recalibration_timer_start is None:
                    recalibration_timer_start = current_time
                    print("⏳ Recalibrating soon...")
                # If held for the required duration, update the pink boxes.
                elif current_time - recalibration_timer_start >= recalibration_hold_time:
                    for idx in tracked_idxs_x:
                        lx = int(lm.landmark[idx].x * w)
                        ly = int(lm.landmark[idx].y * h)
                        pink_boxes[idx] = (lx - dead_zone, lx + dead_zone, ly - dead_zone, ly + dead_zone)
                    print("🔄 Recalibrated.")
                    recalibration_timer_start = None
            else:
                # If the head moves out of the neutral zone, reset the timer.
                recalibration_timer_start = None

    else:
        # --- Sleep Mode Logic ---
        if current_time - last_face_seen_time > sleep_trigger_duration and not sleep_mode:
            print("😴 No face detected. Entering sleep mode...")
            sleep_mode = True

    # --- Display Status on Screen ---
    status_text = "🟢 Scrolling Enabled" if scroll_enabled else "🔴 Scrolling Stopped"
    cv2.putText(frame, status_text, (10, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                (0, 255, 0) if scroll_enabled else (0, 0, 255), 2)

    # Show the video feed unless in sleep mode.
    if not sleep_mode:
        cv2.imshow("🧠 Gaze & Voice Tracker", frame)
        
    # Exit the loop if 'q' is pressed.
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# --- Cleanup ---
cap.release()
cv2.destroyAllWindows()

