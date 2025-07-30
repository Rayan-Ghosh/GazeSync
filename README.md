# GazeSync

A Python-based accessibility tool that enables hands-free computer control using head movements and voice commands. This script is designed to assist users with motor impairments by providing an intuitive way to navigate websites and documents through gaze-tracking and speech recognition.

## Features

* **Dual-Mode Operation**: Choose between a comprehensive **`Voice + Face Tracking`** mode or a simpler **`Voice-Only`** mode.
* **Hands-Free Scrolling**: Navigate vertically and horizontally using head movements.
* **Voice-Activated Controls**: Use verbal commands to start, stop, scroll, zoom, and recalibrate.
* **Intelligent Zoom**: Control browser zoom levels (`zoom in`, `zoom out`, `reset zoom`) with your voice.
* **Automatic Recalibration**: The system intelligently re-centers the dead zone if you hold your head steady in the neutral position.
* **Offline Voice Recognition**: Utilizes the Vosk engine for private, offline command processing without needing an internet connection.
* **Sleep Mode**: Automatically pauses tracking when no face is detected to conserve system resources.

## Requirements

* Python 3.10+
* A standard webcam
* A microphone

## Installation Guide

Follow these steps to set up the project on your local machine.

### 1. Clone the Repository

First, clone this repository to your computer using Git:

```bash
git clone [https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git](https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git)
cd YOUR_REPOSITORY_NAME
```

### 2. Install Dependencies

Install all the required Python libraries using pip. It's recommended to do this within a virtual environment.

```bash
pip install opencv-python mediapipe vosk pyaudio pyautogui
```

### 3. Download the Vosk Voice Model

This tool requires an offline speech recognition model to function.

* **Download the model:** [**vosk-model-small-en-us-0.15.zip**](https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip)
* **Unzip the file.**
* **Place the resulting folder**, named `vosk-model-small-en-us-0.15`, directly inside your project directory. The script is configured to look for it there.

Your final folder structure should look like this:

```
GazeSync/
├── vosk-model-small-en-us-0.15/
└── main.py
```

## How to Run

Once the setup is complete, run the script from your terminal:

```bash
python main.py
```

## Usage Instructions

1.  **Select a Mode**: Upon launching, the terminal will prompt you to choose an operational mode (`1` for Voice-Only, `2` for Voice + Face Tracking).
2.  **Initial Calibration**: If you select face tracking, a camera window will appear. **Hold your head steady and look directly at the camera for 2-3 seconds**. The script will automatically calibrate and print a confirmation message in the terminal.
3.  **Control the System**:
    * **Gaze Scrolling**: Move your head up, down, left, or right beyond the calibrated "dead zone" to scroll.
    * **Voice Commands**: Use the following verbal commands at any time:
        * `"start"` / `"resume"`: Enables all scrolling.
        * `"stop"` / `"pause"`: Disables all scrolling.
        * `"calibrate"` / `"reposition"`: Triggers a manual recalibration.
        * `"zoom in"` / `"zoom out"` / `"reset zoom"`: Controls browser zoom.
        * (In Voice-Only Mode): `"up"`, `"down"`, `"left"`, `"right"`.
4.  **Exiting the Application**: To close the script, make sure the camera window is active and press the **`q`** key on your keyboard.

### ⚠️ Important Note for macOS Users

For the script to control scrolling, you **must** grant Accessibility permissions to your terminal or code editor.

* Go to `System Settings > Privacy & Security > Accessibility`.
* Click the `+` button and add your terminal application (e.g., `Terminal`, `iTerm`) or your code editor (e.g., `Visual Studio Code`) to the list of allowed applications.
