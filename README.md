# Smart Baby Monitoring and Soothing System

## Project Overview

The **Smart Baby Monitoring and Soothing System** is an intelligent, multi-sensory infant monitoring and soothing system developed using a **Raspberry Pi 4**.

The system continuously monitors the baby's condition using:

* Audio-based sound detection
* Eye-state detection
* Servo motor movement
* Light projector patterns
* Automated audio responses

Based on the detected baby state, the system automatically provides an appropriate response such as soothing music, fun sounds, lullabies, mobile movement, or light patterns.

This project is developed following **Human–Computer Interaction (HCI)** principles, with a focus on adaptive interaction between the system and the infant's detected state.

---

## Key Features

### Audio-Based Detection

The system identifies different audio conditions:

* Crying
* Laughing
* Noise
* Silence

### Eye-State Detection

The system detects the baby's eye state:

* **Open eyes** → Awake
* **Closed eyes** → Sleeping

### Automatic Audio Response

Different audio responses are triggered according to the detected state:

* Crying → Soothing music
* Laughing → Fun audio
* Sleeping → Lullaby
* Awake and neutral → No audio response

### Mechanical Motion

A servo motor controls the baby mobile and provides gentle movement according to the detected state.

### Light Projector Integration

The light projector is activated during the laughing/happy state and produces gentle visual patterns.

### Real-Time State Machine

The system uses a real-time state-based approach to dynamically switch between baby states while reducing unnecessary or frequent state changes.

---

## System States

| Detected Condition    | Baby State | System Response                |
| --------------------- | ---------- | ------------------------------ |
| Cry detected          | Crying     | Soothing audio + mobile motion |
| Laugh detected        | Laughing   | Fun audio + light projector    |
| Eyes closed + silence | Sleeping   | Lullaby                        |
| Eyes open + silence   | Awake      | Idle monitoring                |
| Other noise           | Noise      | Monitoring                     |

---

## Technologies Used

### Hardware

* Raspberry Pi 4 Model B
* Raspberry Pi Camera Module
* USB Microphone
* Speaker
* Servo Motor
* Light Projector
* Relay Module

### Software

* Python 3.11
* MediaPipe Face Mesh
* OpenCV
* TensorFlow Lite
* YAMNet
* NumPy
* SoundDevice
* SimpleAudio
* Picamera2
* RPi.GPIO

---

## Project Structure

```text
baby_ai/
│
├── src/
│   ├── main.py
│   ├── eye_worker.py
│   ├── audio_player.py
│   ├── ring_buffer.py
│   ├── servo_controller.py
│   └── light_controller.py
│
├── models/
│   ├── yamnet.tflite
│   └── classifier.tflite
│
├── audio/
│   ├── soothing.wav
│   ├── fun.wav
│   └── lullaby.wav
│
├── requirements.txt
└── README.md
```

---

## System Setup

### Supported Platform

The system is designed and tested on:

* **Raspberry Pi 4 Model B**
* **Raspberry Pi OS (Legacy, 64-bit)**
* **Debian Bookworm Version 12**
* **Python 3.11**

Python 3.11 is used to provide better compatibility with the MediaPipe-based computer vision components of the system.

---

## 1. Clone the Repository

Open the Raspberry Pi terminal and clone the project:

```bash
git clone https://github.com/amaya0617/Baby-Mobile.git
```

Navigate into the project:

```bash
cd Baby-Mobile
```

---

## 2. Create the Virtual Environment

Create the Python virtual environment:

```bash
python3 -m venv baby_venv --system-site-packages
```

Activate the virtual environment:

```bash
source baby_venv/bin/activate
```

Check the Python version:

```bash
python --version
```

The expected version is:

```text
Python 3.11.x
```

---

## 3. Upgrade Python Package Tools

```bash
pip install --upgrade pip setuptools wheel
```

---

## 4. Install Python Dependencies

Install the packages listed in `requirements.txt`:

```bash
pip install -r requirements.txt
```

---

## 5. Install Raspberry Pi System Packages

Deactivate the virtual environment temporarily:

```bash
deactivate
```

Update the Raspberry Pi package list:

```bash
sudo apt update
```

Install the required system packages:

```bash
sudo apt install -y libasound2-dev
```

Install Raspberry Pi GPIO:

```bash
sudo apt install python3-rpi.gpio -y
```

Install Picamera2:

```bash
sudo apt install python3-picamera2 -y
```

Activate the virtual environment again:

```bash
source baby_venv/bin/activate
```

---

## 6. Verify the Installation

Run the following command:

```bash
python - <<EOF
import numpy as np
import cv2
import mediapipe as mp
from picamera2 import Picamera2

print("Python OK")
print("NumPy:", np.__version__)
print("OpenCV:", cv2.__version__)
print("MediaPipe:", mp.__version__)
print("Picamera2 OK")
EOF
```

If the installation is successful, the terminal should display the Python and package versions without import errors.

---

## 7. Add the Required Models

The following model files must be placed inside the `models` directory:

```text
models/
├── yamnet.tflite
└── classifier.tflite
```

Make sure both `.tflite` files are available before running the system.

---

## 8. Add Audio Files

Place the required audio files inside the `audio` directory:

```text
audio/
├── soothing.wav
├── fun.wav
└── lullaby.wav
```

### Audio Requirements

The audio files should be:

* WAV format
* Mono
* 16 kHz sample rate

---

## 9. Booting Up the System

Open the Raspberry Pi terminal.

Navigate to the project directory:

```bash
cd ~/Desktop/baby_ai
```

> **Note:** The above path is an example. Use the actual path where the project is located on your Raspberry Pi.

Activate the virtual environment:

```bash
source baby_venv/bin/activate
```

If you used a different virtual environment name, replace `baby_venv` with your environment name.

Run the main program:

```bash
python src/main.py
```

After running the command, the Smart Baby Monitoring and Soothing System will start.

---

## System Workflow

The overall system follows this general process:

```text
              ┌──────────────────┐
              │   Raspberry Pi   │
              └────────┬─────────┘
                       │
              ┌────────▼─────────┐
              │ Audio + Camera   │
              │     Input        │
              └────────┬─────────┘
                       │
          ┌────────────┴────────────┐
          │                         │
   ┌──────▼───────┐         ┌───────▼──────┐
   │ Audio/YAMNet │         │ Eye Detection│
   │ Classification│         │  MediaPipe   │
   └──────┬───────┘         └───────┬──────┘
          │                         │
          └────────────┬────────────┘
                       │
                ┌──────▼───────┐
                │ State Machine │
                └──────┬───────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
   ┌────▼────┐    ┌────▼────┐    ┌────▼─────┐
   │  Audio  │    │  Servo  │    │  Light   │
   │ Response│    │ Movement│    │ Projector│
   └─────────┘    └─────────┘    └──────────┘
```

---

## Important Notes

* Keep the Raspberry Pi camera properly connected before starting the system.
* Make sure the microphone and speaker are connected.
* Ensure the required `.tflite` models are inside the `models` directory.
* Ensure all required `.wav` files are inside the `audio` directory.
* Activate the virtual environment before running the application.
* The project is intended to run on the specified Raspberry Pi OS and Python environment.


