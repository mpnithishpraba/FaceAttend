# Face Recognition System - Technical Documentation

Prepared from the actual files in this directory scan.

## 1. Project Overview and Problem Statement

This project is a Python desktop face recognition application located under `face recognition/`. It provides real-time webcam face detection, blink-based liveness checking, and face matching against a user-selected reference image.

The application solves a local identity verification problem: a user can load a known reference face image, start a webcam feed, and receive live visual feedback when a detected face matches the reference after passing a blink liveness check.

Actual implementation stack:

| Area | Actual implementation |
|---|---|
| UI | Tkinter desktop application |
| Camera and image processing | OpenCV |
| Face detection | MediaPipe BlazeFace short-range model |
| Face landmarks | MediaPipe FaceLandmarker task model |
| Face recognition | OpenCV SFace ONNX model |
| Rendering | Pillow `ImageTk` inside Tkinter |
| Numerical processing | NumPy |

Important scope note: the scanned project does not contain a React Native app, `package.json`, `services/` directory, SQLite implementation, AWS sync service, or purge service. Those items are therefore documented as not implemented in this codebase.

## 2. Actual Folder Structure

```text
FACE REG/
|-- Face Recognition Technical Documentation.docx
|-- ~$ce Recognition Technical Documentation.docx
|-- technical_documentation.md
|-- presentation.js
`-- face recognition/
    |-- README.md
    |-- requirements.txt
    |-- face_recognition_app.py
    |-- blaze_face_short_range.tflite
    |-- face_landmarker.task
    `-- face_recognition_sface_2021dec.onnx
```

`~$ce Recognition Technical Documentation.docx` is a temporary Microsoft Word lock file, not source code.

## 3. System Architecture Diagram

```text
+-------------------------+
| Tkinter Desktop UI      |
| - reference image panel |
| - camera controls       |
| - live video panel      |
| - detection log/status  |
+-----------+-------------+
            |
            v
+-------------------------+       +------------------------------+
| OpenCV VideoCapture     |       | Reference Image Loader       |
| - webcam index 0/1      |       | - file dialog                |
| - 640 x 480 frames      |       | - image read with cv2.imread |
| - mirrored display      |       | - face crop with margin      |
+-----------+-------------+       +---------------+--------------+
            |                                     |
            v                                     v
+-------------------------+       +------------------------------+
| MediaPipe FaceDetector  |       | FaceComparer.set_reference() |
| BlazeFace TFLite        |       | - MediaPipe landmark align   |
| min confidence 0.5      |       | - OpenCV SFace embedding     |
+-----------+-------------+       +---------------+--------------+
            |                                     |
            v                                     |
+-------------------------+                       |
| Blink Liveness Check    |                       |
| FaceLandmarker landmarks|                       |
| EAR open > 0.25         |                       |
| EAR blink < 0.20        |                       |
| reopen/update > 0.28    |                       |
+-----------+-------------+                       |
            |                                     |
            v                                     v
+-------------------------+       +------------------------------+
| FaceComparer.compare()  +------>| OpenCV SFace Cosine Match    |
| - align face crop       |       | threshold: 50 percent match  |
| - extract live embedding|       | SFace reference: 0.363 score |
+-----------+-------------+       +---------------+--------------+
            |                                     |
            v                                     v
+-------------------------+       +------------------------------+
| Overlay and Status UI   |       | Detection Log                |
| - pending liveness      |       | - timestamped UI events      |
| - match percent         |       +------------------------------+
| - bounding boxes        |
+-------------------------+
```

## 4. Components and Responsibilities

### `face_recognition_app.py`

Main application file. It contains model setup, theme constants, the face comparison engine, the Tkinter UI, camera loop, liveness logic, and application entry point.

| Component | Lines | Responsibility |
|---|---:|---|
| `APP_DIR` | 44 | Resolves the application directory for model paths. |
| `FACE_DETECTOR_MODEL` | 46 | Points to `blaze_face_short_range.tflite`. |
| `FACE_LANDMARKER_MODEL` | 47 | Points to `face_landmarker.task`. |
| `MODEL_URLS` | 49 | Defines download URLs for BlazeFace, FaceLandmarker, and SFace ONNX. |
| `ensure_models()` | 66 | Downloads required model files if missing. |
| `FaceComparer` | 97 | Loads SFace and FaceLandmarker; handles alignment, embeddings, and matching. |
| `FaceRecognitionApp` | 218 | Builds and operates the Tkinter UI and live camera loop. |
| `main()` | 775 | Ensures models exist, starts Tkinter, and handles close event. |

### Model Artifacts

| File | Actual size | Purpose |
|---|---:|---|
| `blaze_face_short_range.tflite` | 229,746 bytes / 0.22 MB | MediaPipe short-range face detector. |
| `face_landmarker.task` | 3,758,596 bytes / 3.58 MB | MediaPipe face landmark model used for SFace alignment and blink liveness. |
| `face_recognition_sface_2021dec.onnx` | 38,696,353 bytes / 36.90 MB | OpenCV SFace model used to produce face embeddings and cosine similarity matches. |

### `README.md`

Describes the app as a real-time face detection and recognition desktop app built with Tkinter, MediaPipe, and OpenCV. The README mentions a two-stage histogram plus FaceMesh approach, but the current source code has moved to OpenCV SFace ONNX embeddings for identity matching.

### `requirements.txt`

Defines the external Python dependencies:

```text
opencv-contrib-python>=4.8.0
mediapipe>=0.10.0
pillow>=10.0.0
numpy>=1.24.0
```

## 5. ML Model Pipeline

Actual pipeline implemented in `face_recognition_app.py`:

```text
Input frame/reference image
        |
        v
MediaPipe FaceDetector
BlazeFace short-range TFLite
        |
        v
Face crop / bounding box
        |
        v
MediaPipe FaceLandmarker
5-point SFace alignment:
RightEye, LeftEye, NoseTip, RightMouth, LeftMouth
        |
        v
OpenCV FaceRecognizerSF
SFace ONNX embedding
        |
        v
Cosine similarity match
        |
        v
Match percent + UI overlay
```

Model names found in code:

| Pipeline step | Actual model/library |
|---|---|
| Detection | `blaze_face_short_range.tflite` through `mp_vision.FaceDetector` |
| Liveness landmarks | `face_landmarker.task` through `mp_vision.FaceLandmarker` |
| Embedding | `face_recognition_sface_2021dec.onnx` through `cv2.FaceRecognizerSF_create` |
| Matching | `cv2.FaceRecognizerSF_FR_COSINE` |

No MobileNetV2 model is present in the scanned codebase.

## 6. Liveness Detection Mechanism

The implemented liveness check is blink-based. Smile and head-turn liveness are not implemented.

Actual state machine:

| State | Meaning |
|---:|---|
| `0` | Waiting for open eyes |
| `1` | Waiting for blink |
| `2` | Liveness passed |

Actual liveness constants and logic:

| Value | Meaning |
|---:|---|
| `avg_ear > 0.25` | Open-eye condition moves state from 0 to 1. |
| `avg_ear < 0.20` | Blink condition while in state 1. |
| `face_h > ref_face_height * 0.90` | Rejects paper-tilt spoof by requiring face height to remain stable during blink. |
| `avg_ear > 0.28` | Updates reference face height after eyes reopen. |
| `no_face_frames > 15` | Resets liveness state when no face is visible for long enough. |

Eye Aspect Ratio landmarks used:

| Eye | Landmarks |
|---|---|
| Left EAR | `159`, `145`, `33`, `133` |
| Right EAR | `386`, `374`, `362`, `263` |

Face height landmarks used for anti-spoof tilt guard:

| Measurement | Landmarks |
|---|---|
| Face height | `10` to `152` |

## 7. Matching Logic

`FaceComparer.compare()` aligns the detected face crop, extracts a live SFace embedding, and compares it to the stored reference embedding with cosine similarity.

Actual code comments and thresholds:

| Item | Actual value |
|---|---:|
| Stored embedding | 128D SFace embedding, per source comment |
| `self.match_threshold` | `0.50` |
| UI match threshold percent | `60%` comment in camera drawing section |
| SFace reference threshold | `0.363` |
| SFace reference accuracy comment | `LFW 99.31% accuracy` |
| Score mapping below `0.363` | Maps to `0..59%` |
| Score mapping `0.363..1.0` | Maps to `60..100%` |

## 8. Offline-First Data Flow and SQLite Schema

No SQLite database or offline-first persistence layer is implemented in the scanned project.

Actual data flow is in-memory and local:

```text
reference image file -> cv2.imread -> detected face crop -> SFace reference embedding in memory
webcam frame -> MediaPipe detection -> blink liveness -> SFace live embedding -> cosine match -> Tkinter UI/log
```

There is no `sqlite3` import, no database file, no schema migration, and no service layer for offline sync.

## 9. AWS Sync and Purge Mechanism

No AWS sync or purge mechanism is implemented in the scanned project.

Evidence from directory scan:

| Requested artifact | Found? |
|---|---|
| AWS SDK / `boto3` | No |
| `SyncService` | No |
| Upload queue | No |
| Purge job/service | No |
| Remote API client | No |

## 10. React Native Integration Steps

No React Native integration exists in the scanned project.

Evidence:

| Requested file or artifact | Found? |
|---|---|
| `package.json` | No |
| `android/` | No |
| `ios/` | No |
| React Native source files | No |
| JavaScript/TypeScript app source | No |

Actual run stack is Python desktop:

```bash
cd "face recognition"
pip install -r requirements.txt
python face_recognition_app.py
```

## 11. API Reference

No `services/` directory exists, so there are no exported service functions to document. The callable API below is derived from the actual Python source.

### Module Functions

| Function | Purpose |
|---|---|
| `ensure_models()` | Downloads missing model files from `MODEL_URLS`, exits on download failure. |
| `main()` | Calls `ensure_models()`, creates the Tkinter root, instantiates `FaceRecognitionApp`, and starts `root.mainloop()`. |

### `FaceComparer`

| Method | Purpose |
|---|---|
| `__init__()` | Creates OpenCV SFace recognizer and MediaPipe FaceLandmarker; initializes reference state and match threshold. |
| `_get_sface_alignment(img_bgr)` | Uses FaceLandmarker to extract five alignment points in OpenCV SFace 15-float format. |
| `set_reference(img_bgr)` | Aligns the reference face crop and stores the reference SFace embedding. Returns `True` or `False`. |
| `compare(face_bgr)` | Aligns a live face crop, extracts its SFace embedding, computes cosine match score, maps it to a match percentage, and returns `(is_match, match_percent)`. |

### `FaceRecognitionApp`

| Method | Purpose |
|---|---|
| `__init__(root)` | Initializes UI state, liveness state, MediaPipe FaceDetector, `FaceComparer`, and layout. |
| `_build_ui()` | Builds header, reference panel, camera controls, detection log, video panel, and status bar. |
| `_section_label(parent, text)` | Adds a styled section label. |
| `_make_button(parent, text, command, color)` | Adds a styled Tkinter button with hover behavior. |
| `_separator(parent)` | Adds a horizontal separator. |
| `_lighten(hex_color, factor=0.15)` | Returns a lightened hex color for button hover effects. |
| `_center_window()` | Centers the 1100 x 750 window. |
| `_tick_clock()` | Updates the header clock once per second. |
| `_log(msg)` | Appends timestamped events to the detection log widget. |
| `_load_reference()` | Opens a file dialog, reads an image, detects a face, crops it, stores the reference embedding, and updates the UI. |
| `_start_camera()` | Opens webcam index 0 or 1, configures 640 x 480 capture, validates frame reading, and starts the background camera thread. |
| `_stop_camera()` | Stops capture, releases the camera, resets UI status, and logs the stop event. |
| `_camera_loop()` | Reads frames, runs face detection, liveness, throttled comparison every 5 frames, overlays labels/boxes, and schedules UI updates. |
| `_update_frame(photo, num_faces)` | Updates the displayed frame, face count, and status label. |
| `_fit_image(img, max_w, max_h)` | Resizes a PIL image to fit the available video panel while preserving aspect ratio. |
| `_set_status(text, color=TEXT_SECONDARY)` | Updates the status text and icon color. |
| `on_closing()` | Stops camera and destroys the root window. |

## 12. Performance Benchmarks and Constants

No measured latency benchmark is present in the code. The table below uses only constants, comments, and file sizes actually found in the project.

| Metric | Actual value found | Source |
|---|---:|---|
| Detector model size | 0.22 MB | File size |
| Face landmarker model size | 3.58 MB | File size |
| SFace recognition model size | 36.90 MB | File size |
| Total model artifact size | 40.70 MB | Sum of three model files |
| Camera capture resolution | 640 x 480 | `_start_camera()` |
| Face detection confidence | 0.5 | `FaceDetectorOptions` |
| Face landmark detection confidence | 0.5 | `FaceLandmarkerOptions` |
| Face presence confidence | 0.5 | `FaceLandmarkerOptions` |
| Tracking confidence | 0.5 | `FaceLandmarkerOptions` |
| Recognition frequency | Every 5 frames | `_camera_loop()` |
| Match threshold | 50% internal threshold | `FaceComparer.__init__()` |
| SFace threshold reference | 0.363 | Source comment |
| Accuracy reference | LFW 99.31% | Source comment |
| Latency | Not measured in code | Not found |

The current recognition model is not under 20 MB; `face_recognition_sface_2021dec.onnx` is 36.90 MB.

## 13. Build and Run Instructions

No `package.json` scripts are present. Actual build/run instructions come from `README.md` and `requirements.txt`.

```bash
cd "face recognition"
pip install -r requirements.txt
python face_recognition_app.py
```

Models are automatically downloaded by `ensure_models()` if they are missing:

| Model | URL source in code |
|---|---|
| BlazeFace short range | `storage.googleapis.com/mediapipe-models/face_detector/...` |
| FaceLandmarker | `storage.googleapis.com/mediapipe-models/face_landmarker/...` |
| SFace ONNX | `github.com/opencv/opencv_zoo/.../face_recognition_sface_2021dec.onnx` |

## 14. Known Gaps Against the Requested Target Architecture

| Requested item | Status in scanned codebase |
|---|---|
| React Native application | Not present |
| MobileNetV2 model | Not present |
| SQLite schema | Not present |
| AWS sync queue/upload/purge | Not present |
| `services/` exported APIs | Not present |
| Measured latency benchmark | Not present |
| Model size under 20 MB | Not true for current SFace ONNX model |
| Smile liveness | Not present |
| Head-turn liveness | Not present |

## 15. Summary

The actual project is a local Python desktop face recognition application with a clear edge-AI pipeline: MediaPipe BlazeFace detects faces, MediaPipe FaceLandmarker provides landmarks for SFace alignment and blink liveness, and OpenCV SFace ONNX performs embedding and cosine matching. The implementation is fully local and webcam-driven, but it does not currently include the React Native, SQLite, AWS sync, or service-layer architecture described in the requested target deliverables.
