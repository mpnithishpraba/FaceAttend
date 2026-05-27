"""
Face Recognition App — Real-Time Webcam Detection & Recognition
================================================================
A Tkinter desktop application that performs real-time face detection
and recognition using the system webcam.

Uses:
  • MediaPipe Tasks API  → Face detection + Face landmarks
  • OpenCV               → Webcam capture, image processing, histogram comparison
  • Pillow               → Tk image rendering

No dlib, TensorFlow, or face_recognition needed. Works on Python 3.12–3.14.

Dependencies:
    pip install opencv-contrib-python mediapipe pillow numpy

Models (auto-downloaded on first run):
    blaze_face_short_range.tflite
    face_landmarker.task

Usage:
    python face_recognition_app.py
"""

import os
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime
import urllib.request

import cv2
import numpy as np
from PIL import Image, ImageTk

import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision as mp_vision

# ──────────────────────────────────────────────
# Model paths & auto-download
# ──────────────────────────────────────────────
APP_DIR = os.path.dirname(os.path.abspath(__file__))

FACE_DETECTOR_MODEL   = os.path.join(APP_DIR, "blaze_face_short_range.tflite")
FACE_LANDMARKER_MODEL = os.path.join(APP_DIR, "face_landmarker.task")

MODEL_URLS = {
    FACE_DETECTOR_MODEL: (
        "https://storage.googleapis.com/mediapipe-models/"
        "face_detector/blaze_face_short_range/float16/1/"
        "blaze_face_short_range.tflite"
    ),
    FACE_LANDMARKER_MODEL: (
        "https://storage.googleapis.com/mediapipe-models/"
        "face_landmarker/face_landmarker/float16/1/"
        "face_landmarker.task"
    ),
    os.path.join(APP_DIR, "face_recognition_sface_2021dec.onnx"): (
        "https://github.com/opencv/opencv_zoo/raw/main/models/face_recognition_sface/face_recognition_sface_2021dec.onnx"
    ),
}


def ensure_models():
    """Download model files if they don't exist."""
    for path, url in MODEL_URLS.items():
        if not os.path.exists(path):
            print(f"Downloading {os.path.basename(path)} …")
            try:
                urllib.request.urlretrieve(url, path)
                print(f"  ✓ Saved to {path}")
            except Exception as e:
                print(f"  ✗ Download failed: {e}")
                print(f"    Please download manually from:\n    {url}")
                sys.exit(1)


# ──────────────────────────────────────────────
# Theme / Style Constants
# ──────────────────────────────────────────────
BG_PRIMARY     = "#0f1117"
BG_SECONDARY   = "#1a1d27"
BG_TERTIARY    = "#252836"
ACCENT         = "#6c63ff"
GREEN          = "#2ecc71"
RED            = "#e74c3c"
YELLOW         = "#f1c40f"
TEXT_PRIMARY   = "#eaeaea"
TEXT_SECONDARY = "#8e8e9a"
FONT_FAMILY    = "Segoe UI"
BORDER_COLOR   = "#2d3040"


# ──────────────────────────────────────────────
class FaceComparer:
    """
    Compare faces using an aggressive Fusion technique:
      1. OpenCV's cutting-edge SFace (ONNX Deep Learning) for master-tier Identity Matching.
      2. MediaPipe Dense Mesh Extraction exclusively for Liveness/Anti-Spoofing checks.
    """

    def __init__(self):
        # We initialize the SFace Deep Learning ONNX model here
        SFACE_PATH = os.path.join(APP_DIR, "face_recognition_sface_2021dec.onnx")
        try:
            self.recognizer = cv2.FaceRecognizerSF_create(SFACE_PATH, "")
        except Exception as e:
            print(f"Failed to load SFace model: {e}")
            self.recognizer = None
            
        self.ref_loaded = False
        self.ref_features = None  # Holds 128D SFace embedding
        self.match_threshold = 0.50    # SFace typically matches > 0.36 cosine

        # Create FaceLandmarker strictly for structural liveness (blink) tracking
        try:
            landmarker_options = mp_vision.FaceLandmarkerOptions(
                base_options=mp_python.BaseOptions(
                    model_asset_path=FACE_LANDMARKER_MODEL
                ),
                running_mode=mp_vision.RunningMode.IMAGE,
                num_faces=1,
                min_face_detection_confidence=0.5,
                min_face_presence_confidence=0.5,
                min_tracking_confidence=0.5,
                output_face_blendshapes=False,
                output_facial_transformation_matrixes=False,
            )
            self.landmarker = mp_vision.FaceLandmarker.create_from_options(
                landmarker_options
            )
        except Exception as e:
            print(f"FaceLandmarker init warning: {e}")
            self.landmarker = None

    def _get_sface_alignment(self, img_bgr):
        """Extracts the exact 5 points needed by SFace using MediaPipe."""
        if self.landmarker is None: return None
        try:
            rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
            mp_img = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
            result = self.landmarker.detect(mp_img)
            if not result.face_landmarks: return None
            
            lm = result.face_landmarks[0]
            h, w = img_bgr.shape[:2]
            
            # SFace expects subject's [RightEye, LeftEye, NoseTip, RightMouth, LeftMouth]
            # MediaPipe indices: 33 (RightEye outer), 263 (LeftEye outer), 1 (Nose), 61 (RightMouth), 291 (LeftMouth)
            re_x, re_y = lm[33].x * w, lm[33].y * h
            le_x, le_y = lm[263].x * w, lm[263].y * h
            nt_x, nt_y = lm[1].x * w, lm[1].y * h
            rm_x, rm_y = lm[61].x * w, lm[61].y * h
            lm_x, lm_y = lm[291].x * w, lm[291].y * h
            
            # Construct a dummy bounding box covering the central facial features
            xs = [re_x, le_x, nt_x, rm_x, lm_x]
            ys = [re_y, le_y, nt_y, rm_y, lm_y]
            bx, by = min(xs) - 20, min(ys) - 20
            bw, bh = (max(xs) - min(xs)) + 40, (max(ys) - min(ys)) + 40
            
            # OpenCV SFace 15-float format
            return np.array([bx, by, bw, bh, re_x, re_y, le_x, le_y, nt_x, nt_y, rm_x, rm_y, lm_x, lm_y, 1.0], dtype=np.float32)
        except Exception:
            return None

    def set_reference(self, img_bgr: np.ndarray) -> bool:
        """Extract the 128D Deep Learning embedding from the reference."""
        if self.recognizer is None: return False
        
        align_arr = self._get_sface_alignment(img_bgr)
        if align_arr is None: return False
        
        try:
            aligned_face = self.recognizer.alignCrop(img_bgr, align_arr)
            self.ref_features = self.recognizer.feature(aligned_face)
            self.ref_loaded = True
            return True
        except Exception:
            return False

    def compare(self, face_bgr: np.ndarray) -> tuple:
        """
        Compare using cutting-edge SFace AI models.
        """
        if not self.ref_loaded or self.recognizer is None or self.ref_features is None:
            return False, 0.0

        try:
            align_arr = self._get_sface_alignment(face_bgr)
            if align_arr is None: return False, 0.0
            
            aligned_sys = self.recognizer.alignCrop(face_bgr, align_arr)
            live_feat = self.recognizer.feature(aligned_sys)
            
            # Match strictly uses SFace Cosine Distance (0 to 1, higher is closer)
            score = self.recognizer.match(self.ref_features, live_feat, cv2.FaceRecognizerSF_FR_COSINE)
            
            # Typical matching threshold for SFace is 0.363 for LFW 99.31% accuracy
            # Let's map 0.363 -> 60%, 1.0 -> 100%, 0.0 -> 0%
            if score < 0.363:
                match_percent = max(0.0, (score / 0.363) * 59.0)
            else:
                match_percent = 60.0 + ((score - 0.363) / (1.0 - 0.363)) * 40.0
                
            is_match = match_percent >= (self.match_threshold * 100)
            return is_match, match_percent
            
        except Exception as e:
            return False, 0.0


# ──────────────────────────────────────────────
# Main Application Class
# ──────────────────────────────────────────────
class FaceRecognitionApp:

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Smart Hire AI — Face Recognition")
        self.root.configure(bg=BG_PRIMARY)
        self.root.resizable(True, True)

        # State
        self.cap = None
        self.running = False
        self.thread = None
        self.ref_loaded = False
        self.ref_photo = None
        self.frame_photo = None
        
        # Security State
        self.liveness_state = 0   # 0: waiting for open eyes, 1: waiting for blink, 2: liveness passed
        self.no_face_frames = 0

        # Face detector (MediaPipe Tasks API)
        detector_options = mp_vision.FaceDetectorOptions(
            base_options=mp_python.BaseOptions(
                model_asset_path=FACE_DETECTOR_MODEL
            ),
            running_mode=mp_vision.RunningMode.IMAGE,
            min_detection_confidence=0.5,
        )
        self.detector = mp_vision.FaceDetector.create_from_options(
            detector_options
        )

        # Face comparer
        self.comparer = FaceComparer()

        self._build_ui()
        self._center_window()

    # ──────────────────────────────────────
    # UI Construction  (FIXED LAYOUT)
    # ──────────────────────────────────────
    def _build_ui(self):

        # ── Header ────────────────────────
        header = tk.Frame(self.root, bg=BG_SECONDARY, height=56)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header, text="⬢  Face Recognition System",
            font=(FONT_FAMILY, 15, "bold"),
            fg=ACCENT, bg=BG_SECONDARY
        ).pack(side="left", padx=20, pady=10)

        self.time_label = tk.Label(
            header, text="", font=(FONT_FAMILY, 10),
            fg=TEXT_SECONDARY, bg=BG_SECONDARY
        )
        self.time_label.pack(side="right", padx=20)
        self._tick_clock()

        # ── Main container ────────────────
        main = tk.Frame(self.root, bg=BG_PRIMARY)
        main.pack(fill="both", expand=True, padx=12, pady=8)

        # ─── LEFT PANEL (scrollable-safe, no pack_propagate(False)) ───
        left = tk.Frame(main, bg=BG_SECONDARY, width=280,
                        highlightbackground=BORDER_COLOR,
                        highlightthickness=1)
        left.pack(side="left", fill="y", padx=(0, 10))

        # Section: Reference Image
        self._section_label(left, "REFERENCE IMAGE")

        # Use a fixed-pixel-size frame for the image preview
        ref_frame = tk.Frame(left, bg=BG_TERTIARY, width=240, height=140)
        ref_frame.pack(padx=16, pady=(2, 6))
        ref_frame.pack_propagate(False)

        self.ref_canvas = tk.Label(
            ref_frame, bg=BG_TERTIARY,
            text="No image loaded",
            fg=TEXT_SECONDARY, font=(FONT_FAMILY, 9),
            anchor="center"
        )
        self.ref_canvas.pack(fill="both", expand=True)

        self.ref_status = tk.Label(
            left, text="Select a face photo for matching",
            font=(FONT_FAMILY, 8), fg=TEXT_SECONDARY,
            bg=BG_SECONDARY, wraplength=240, justify="left"
        )
        self.ref_status.pack(padx=16, anchor="w", pady=(0, 4))

        self._make_button(left, "📂  Load Reference Image",
                          self._load_reference, ACCENT)

        self._separator(left)

        # Section: Camera Controls
        self._section_label(left, "CAMERA CONTROLS")

        self._make_button(left, "▶  Start Camera",
                          self._start_camera, GREEN)
        self._make_button(left, "■  Stop Camera",
                          self._stop_camera, RED)

        self._separator(left)

        # Section: Detection Log
        self._section_label(left, "DETECTION LOG")

        self.log_text = tk.Text(
            left, bg=BG_TERTIARY, fg=TEXT_SECONDARY,
            font=(FONT_FAMILY, 8), height=6,
            relief="flat", wrap="word",
            highlightthickness=0,
            insertbackground=TEXT_PRIMARY
        )
        self.log_text.pack(padx=16, pady=(2, 12), fill="x")
        self.log_text.config(state="disabled")

        # ─── RIGHT PANEL (video feed) ────
        right = tk.Frame(main, bg=BG_SECONDARY,
                         highlightbackground=BORDER_COLOR,
                         highlightthickness=1)
        right.pack(side="left", fill="both", expand=True)

        self.video_label = tk.Label(
            right, bg="#000000",
            text="Camera feed will appear here\n\nClick  ▶ Start Camera  to begin",
            fg=TEXT_SECONDARY,
            font=(FONT_FAMILY, 13),
            anchor="center",
            compound="center"
        )
        self.video_label.pack(fill="both", expand=True, padx=4, pady=4)

        # ── Status bar ────────────────────
        status_bar = tk.Frame(self.root, bg=BG_TERTIARY, height=34)
        status_bar.pack(fill="x", side="bottom")
        status_bar.pack_propagate(False)

        self.status_icon = tk.Label(
            status_bar, text="●", fg=RED,
            bg=BG_TERTIARY, font=(FONT_FAMILY, 10)
        )
        self.status_icon.pack(side="left", padx=(16, 4), pady=5)

        self.status_label = tk.Label(
            status_bar, text="Camera Stopped",
            font=(FONT_FAMILY, 10), fg=TEXT_SECONDARY,
            bg=BG_TERTIARY, anchor="w"
        )
        self.status_label.pack(side="left", pady=5)

        self.face_count_label = tk.Label(
            status_bar, text="Faces: 0",
            font=(FONT_FAMILY, 10), fg=TEXT_SECONDARY,
            bg=BG_TERTIARY
        )
        self.face_count_label.pack(side="right", padx=16, pady=5)

    # ── UI helpers ──────────────────────────
    def _section_label(self, parent, text):
        tk.Label(
            parent, text=text,
            font=(FONT_FAMILY, 9, "bold"),
            fg=TEXT_SECONDARY, bg=BG_SECONDARY, anchor="w"
        ).pack(padx=16, pady=(10, 2), anchor="w")

    def _make_button(self, parent, text, command, color):
        btn = tk.Button(
            parent, text=text, command=command,
            font=(FONT_FAMILY, 10, "bold"),
            fg="#ffffff", bg=color,
            activebackground=color, activeforeground="#ffffff",
            relief="flat", cursor="hand2", padx=10, pady=5
        )
        btn.pack(padx=16, pady=3, fill="x")
        btn.bind("<Enter>",
                 lambda e, b=btn, c=color: b.config(bg=self._lighten(c)))
        btn.bind("<Leave>",
                 lambda e, b=btn, c=color: b.config(bg=c))
        return btn

    def _separator(self, parent):
        tk.Frame(parent, bg=BORDER_COLOR, height=1).pack(
            fill="x", padx=16, pady=6)

    @staticmethod
    def _lighten(hex_color, factor=0.15):
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)
        r = min(255, int(r + (255 - r) * factor))
        g = min(255, int(g + (255 - g) * factor))
        b = min(255, int(b + (255 - b) * factor))
        return f"#{r:02x}{g:02x}{b:02x}"

    def _center_window(self):
        self.root.update_idletasks()
        w, h = 1100, 750
        x = (self.root.winfo_screenwidth() - w) // 2
        y = max(0, (self.root.winfo_screenheight() - h) // 2 - 30)
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    def _tick_clock(self):
        now = datetime.now().strftime("%I:%M:%S %p")
        self.time_label.config(text=now)
        self.root.after(1000, self._tick_clock)

    def _log(self, msg):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.config(state="normal")
        self.log_text.insert("end", f"[{timestamp}] {msg}\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")

    # ──────────────────────────────────────
    # Reference Image
    # ──────────────────────────────────────
    def _load_reference(self):
        path = filedialog.askopenfilename(
            title="Select Reference Face Image",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.bmp"),
                ("All files", "*.*")
            ]
        )
        if not path:
            return

        try:
            img_bgr = cv2.imread(path)
            if img_bgr is None:
                messagebox.showerror("Error", "Could not read the image file.")
                return

            # Detect face in reference using MediaPipe Tasks
            rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
            mp_img = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
            result = self.detector.detect(mp_img)

            if not result.detections:
                messagebox.showwarning(
                    "No Face Found",
                    "Could not detect a face in the selected image.\n"
                    "Please choose a clear, front-facing photo."
                )
                return

            # Crop first detected face
            det = result.detections[0]
            bbox = det.bounding_box
            h_img, w_img = img_bgr.shape[:2]

            margin_x = int(bbox.width * 0.15)
            margin_y = int(bbox.height * 0.15)
            x1 = max(0, bbox.origin_x - margin_x)
            y1 = max(0, bbox.origin_y - margin_y)
            x2 = min(w_img, bbox.origin_x + bbox.width + margin_x)
            y2 = min(h_img, bbox.origin_y + bbox.height + margin_y)

            face_crop = img_bgr[y1:y2, x1:x2]
            self.comparer.set_reference(face_crop)
            self.ref_loaded = True

            # Show thumbnail in sidebar
            pil_img = Image.open(path)
            pil_img.thumbnail((240, 140))
            self.ref_photo = ImageTk.PhotoImage(pil_img)
            self.ref_canvas.config(image=self.ref_photo, text="")

            name = os.path.basename(path)
            self.ref_status.config(text=f"✓ Loaded: {name}", fg=GREEN)
            self._set_status("Reference loaded ✓", GREEN)
            self._log(f"Reference loaded: {name}")

        except Exception as exc:
            messagebox.showerror("Error", f"Failed to load image:\n{exc}")

    # ──────────────────────────────────────
    # Camera Controls
    # ──────────────────────────────────────
    def _start_camera(self):
        if self.running:
            self._set_status("Camera already running", YELLOW)
            return

        self._log("Opening camera…")
        self._set_status("Opening camera…", YELLOW)

        # Try DirectShow first (Windows), then fallback
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not self.cap or not self.cap.isOpened():
            self.cap = cv2.VideoCapture(0)

        if not self.cap or not self.cap.isOpened():
            # Try camera index 1
            self.cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)

        if not self.cap or not self.cap.isOpened():
            self.cap = cv2.VideoCapture(1)

        if not self.cap or not self.cap.isOpened():
            messagebox.showerror(
                "Camera Error",
                "Could not open the webcam.\n\n"
                "Possible fixes:\n"
                "• Make sure a camera is connected\n"
                "• Close other apps using the camera\n"
                "• Check camera permissions in Windows Settings\n"
                "  (Settings → Privacy → Camera)"
            )
            self.cap = None
            self._set_status("Camera not found", RED)
            self._log("ERROR: Camera not found")
            return

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        # Verify we can read a frame
        ret, test_frame = self.cap.read()
        if not ret:
            messagebox.showerror(
                "Camera Error",
                "Camera opened but cannot read frames.\n"
                "Try closing other apps that use the camera."
            )
            self.cap.release()
            self.cap = None
            self._set_status("Camera read failed", RED)
            return

        self.running = True
        self._set_status("Camera Running", GREEN)
        self._log("Camera started successfully")

        self.thread = threading.Thread(target=self._camera_loop, daemon=True)
        self.thread.start()

    def _stop_camera(self):
        self.running = False
        if self.cap and self.cap.isOpened():
            self.cap.release()
            self.cap = None
        self._set_status("Camera Stopped", RED)
        self.face_count_label.config(text="Faces: 0")
        self.video_label.config(
            image="",
            text="Camera feed will appear here\n\nClick  ▶ Start Camera  to begin"
        )
        self.root.after(0, lambda: self._log("Camera stopped"))

    # ──────────────────────────────────────
    # Camera Loop (background thread)
    # ──────────────────────────────────────
    def _camera_loop(self):
        compare_every = 5
        frame_counter = 0
        cached_results = []

        while self.running:
            if self.cap is None or not self.cap.isOpened():
                break

            ret, frame = self.cap.read()
            if not ret:
                self.root.after(0, lambda: self._set_status(
                    "Failed to read frame", RED))
                self.root.after(0, lambda: self._log("ERROR: Lost camera feed"))
                break

            frame = cv2.flip(frame, 1)
            h, w = frame.shape[:2]
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # ── Face detection (MediaPipe Tasks API) ──
            mp_img = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
            det_result = self.detector.detect(mp_img)
            detections = det_result.detections if det_result.detections else []

            frame_counter += 1

            current_boxes = []
            for det in detections:
                bbox = det.bounding_box
                x1 = max(0, bbox.origin_x)
                y1 = max(0, bbox.origin_y)
                x2 = min(w, bbox.origin_x + bbox.width)
                y2 = min(h, bbox.origin_y + bbox.height)
                current_boxes.append((x1, y1, x2, y2))

            # ── Liveness / Anti-Spoofing Detection ──
            if not current_boxes:
                self.no_face_frames += 1
                if self.no_face_frames > 15:
                    self.liveness_state = 0
            else:
                self.no_face_frames = 0
                if self.liveness_state != 2:
                    try:
                        lm_res = self.comparer.landmarker.detect(mp_img)
                        if lm_res and lm_res.face_landmarks:
                            lm = lm_res.face_landmarks[0]
                            def ear(t, b, l, r):
                                v = np.sqrt((lm[t].x - lm[b].x)**2 + (lm[t].y - lm[b].y)**2)
                                hz = np.sqrt((lm[l].x - lm[r].x)**2 + (lm[l].y - lm[r].y)**2)
                                return v / (hz + 1e-6)
                            left_ear = ear(159, 145, 33, 133)
                            right_ear = ear(386, 374, 362, 263)
                            avg_ear = (left_ear + right_ear) / 2.0
                            
                            # Get overall face height
                            face_h = np.sqrt((lm[10].x - lm[152].x)**2 + (lm[10].y - lm[152].y)**2)
                            
                            if self.liveness_state == 0 and avg_ear > 0.25:
                                self.liveness_state = 1
                                self.ref_face_height = face_h  # Save the open-eye face height!
                            elif self.liveness_state == 1:
                                if avg_ear < 0.20:
                                    if hasattr(self, 'ref_face_height'):
                                        # If face height shrank drastically, they titled the paper!
                                        if face_h > self.ref_face_height * 0.90:
                                            self.liveness_state = 2
                                            self.root.after(0, lambda: self._log("🟢 Real face confirmed (Valid Blink)"))
                                        else:
                                            # Reset state because paper tilt was detected
                                            self.liveness_state = 0
                                            self.root.after(0, lambda: self._log("🔴 Spoof Check Failed: Paper Tilt Detected"))
                                elif avg_ear > 0.28:
                                    # Update reference height if they move closer/further while eyes are open
                                    self.ref_face_height = max(getattr(self, 'ref_face_height', face_h), face_h)
                    except Exception:
                        pass

            # ── Face comparison every N frames ──
            if frame_counter % compare_every == 0:
                new_results = []
                for (x1, y1, x2, y2) in current_boxes:
                    if self.ref_loaded:
                        face_crop = frame[y1:y2, x1:x2]
                        if face_crop.size > 0:
                            is_match, match_pct = self.comparer.compare(face_crop)
                            label = "MATCH"
                        else:
                            label, match_pct = "DETECTED", 0.0
                    else:
                        label, match_pct = "DETECTED", 0.0
                    new_results.append((x1, y1, x2, y2, label, match_pct))
                cached_results = new_results
            else:
                new_results = []
                for i, (x1, y1, x2, y2) in enumerate(current_boxes):
                    if i < len(cached_results):
                        _, _, _, _, label, conf = cached_results[i]
                    else:
                        label, conf = "DETECTED", 0.0
                    new_results.append((x1, y1, x2, y2, label, conf))
                cached_results = new_results

            # ── Draw bounding boxes ──────────────
            match_threshold_pct = self.comparer.match_threshold * 100  # 60%
            display = frame.copy()
            for (x1, y1, x2, y2, label, match_pct) in cached_results:
                if self.liveness_state != 2:
                    color_bgr = (0, 140, 255)          # ORANGE — Pending Liveness
                    tag = "SPOOF CHECK: PLEASE BLINK"
                else:
                    if label == "MATCH":
                        if match_pct >= match_threshold_pct:
                            color_bgr = (0, 200, 80)      # GREEN — match >= 60%
                        else:
                            color_bgr = (0, 70, 230)       # RED — match < 60%
                    else:
                        color_bgr = (0, 200, 245)          # YELLOW — no ref loaded

                    if label == "MATCH":
                        tag = f"MATCH  {match_pct:.0f}%"
                    else:
                        tag = "DETECTED (LIVE)"

                cv2.rectangle(display, (x1, y1), (x2, y2), color_bgr, 1)

                corner_len = min(20, (x2 - x1) // 4)
                for cx, cy, dx, dy in [
                    (x1, y1, 1, 1), (x2, y1, -1, 1),
                    (x1, y2, 1, -1), (x2, y2, -1, -1)
                ]:
                    cv2.line(display, (cx, cy),
                             (cx + corner_len * dx, cy), color_bgr, 3)
                    cv2.line(display, (cx, cy),
                             (cx, cy + corner_len * dy), color_bgr, 3)

                (tw, th_t), _ = cv2.getTextSize(
                    tag, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 2)
                cv2.rectangle(
                    display, (x1, y1 - th_t - 14),
                    (x1 + tw + 10, y1), color_bgr, -1)
                cv2.putText(
                    display, tag, (x1 + 5, y1 - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55,
                    (255, 255, 255), 2)

            # ── Convert to Tk image ──────────────
            rgb_out = cv2.cvtColor(display, cv2.COLOR_BGR2RGB)
            pil_frame = Image.fromarray(rgb_out)

            try:
                lw = self.video_label.winfo_width()
                lh = self.video_label.winfo_height()
                if lw > 10 and lh > 10:
                    pil_frame = self._fit_image(pil_frame, lw, lh)
            except Exception:
                pass

            photo = ImageTk.PhotoImage(pil_frame)
            num_faces = len(cached_results)
            self.root.after(0, self._update_frame, photo, num_faces)

        if self.cap and self.cap.isOpened():
            self.cap.release()

    def _update_frame(self, photo, num_faces):
        self.frame_photo = photo
        self.video_label.config(image=photo, text="")
        self.face_count_label.config(text=f"Faces: {num_faces}")

        if num_faces == 0:
            self._set_status("No Face Detected", YELLOW)
        elif getattr(self, "liveness_state", 0) != 2:
            self._set_status("Spoof Check: Please blink to confirm liveness", YELLOW)
        elif self.ref_loaded:
            self._set_status("Scanning & Comparing…", GREEN)
        else:
            self._set_status(f"Detected {num_faces} face(s) - LIVE", GREEN)

    @staticmethod
    def _fit_image(img: Image.Image, max_w: int, max_h: int) -> Image.Image:
        ratio = min(max_w / img.width, max_h / img.height)
        new_size = (int(img.width * ratio), int(img.height * ratio))
        return img.resize(new_size, Image.LANCZOS)

    def _set_status(self, text, color=TEXT_SECONDARY):
        self.status_label.config(text=text, fg=color)
        self.status_icon.config(fg=color)

    def on_closing(self):
        self._stop_camera()
        self.root.destroy()


# ──────────────────────────────────────────────
# Entry Point
# ──────────────────────────────────────────────
def main():
    ensure_models()
    root = tk.Tk()
    app = FaceRecognitionApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
