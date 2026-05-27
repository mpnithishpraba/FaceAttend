# Face Recognition System

Real-time face detection & recognition desktop app built with **Tkinter**, **MediaPipe**, and **OpenCV**.

> No dlib or TensorFlow required — installs cleanly on Python 3.12–3.14.

## Features

| Feature | Description |
|---|---|
| 🎥 Live Webcam Feed | Displayed inside the Tkinter window (not a separate OpenCV window) |
| 🔍 Face Detection | MediaPipe BlazeFace — fast, GPU-free |
| ✅ Face Matching | Histogram correlation + FaceMesh structural features |
| 🟩 Green Box | Match — labelled **"YOU"** with confidence % |
| 🟥 Red Box | No match — labelled **"UNKNOWN"** |
| 📋 Detection Log | Timestamped event log in the sidebar |
| 🧵 Threaded | Camera runs in a background thread (no UI freeze) |

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the app
python face_recognition_app.py
```

## Usage

1. **Load Reference Image** — click the button and select a clear, front-facing photo (e.g. `me.jpg`).
2. **Start Camera** — opens the webcam; faces are detected and compared in real time.
3. Matching faces → **green** bounding box with "YOU" label.
   Unknown faces → **red** bounding box with "UNKNOWN" label.
4. **Stop Camera** — safely releases the webcam.

## Dependencies

| Package | Purpose |
|---|---|
| `opencv-contrib-python` | Webcam capture, image processing, histogram comparison |
| `mediapipe` | Face detection (BlazeFace) + FaceMesh landmarks |
| `pillow` | Image rendering in Tkinter |
| `numpy` | Array operations |

## How Recognition Works

Since `dlib` / `face_recognition` / `TensorFlow` don't support Python 3.14 yet, this app uses a lightweight two-stage comparison:

1. **Appearance** — HSV histogram correlation between the reference face crop and each detected face.
2. **Structure** — Geometric ratios between key FaceMesh landmarks (eyes, nose, mouth, chin) normalised by face width.

The two scores are combined (60% appearance / 40% structure) to produce a final similarity score.
