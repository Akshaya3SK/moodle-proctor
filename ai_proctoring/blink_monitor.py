"""
Blink Rate Monitor
Uses Eye Aspect Ratio (EAR) from MediaPipe FaceLandmarker to detect blinks.

Suspicious patterns (moderate mode):
  - Very LOW blink rate  (<3 blinks/min) → candidate may be staring at notes
  - Very HIGH blink rate (>40 blinks/min) → stress / rapid eye movement

Normal blink rate: 10–20 blinks per minute.
"""

import cv2
import time
import numpy as np
from collections import deque

import config as C
from violation_logger import ViolationLogger, ViolationType
from utils import capture_screenshot


# ─── Tuning ───────────────────────────────────────────────────────────────────
EAR_THRESHOLD        = C.BLINK_EAR_THRESHOLD
EAR_CONSEC_FRAMES    = C.BLINK_EAR_CONSEC_FRAMES
MEASURE_WINDOW_SEC   = 60.0   # Rolling window for BPM calculation
LOW_BLINK_THRESHOLD  = C.LOW_BLINK_THRESHOLD
HIGH_BLINK_THRESHOLD = C.HIGH_BLINK_THRESHOLD
MIN_OBSERVATION_SEC  = C.BLINK_MIN_OBSERVATION_SEC
LOW_RATE_GRACE_SEC   = C.BLINK_LOW_RATE_GRACE_SEC
ANOMALY_STREAK_REQ   = C.BLINK_RATE_ANOMALY_STREAK
BASELINE_SEC         = C.BLINK_BASELINE_SEC
EVENT_COOLDOWN_SEC   = C.BLINK_EVENT_COOLDOWN_SEC

# MediaPipe FaceLandmarker landmark indices for left & right eye
# Left eye:  [362, 385, 387, 263, 373, 380]
# Right eye: [33,  160, 158, 133, 153, 144]
LEFT_EYE_IDX  = [362, 385, 387, 263, 373, 380]
RIGHT_EYE_IDX = [33,  160, 158, 133, 153, 144]


def _ear(landmarks, eye_indices, w, h) -> float:
    """Calculate Eye Aspect Ratio for 6 landmark points."""
    pts = np.array([
        [landmarks[i].x * w, landmarks[i].y * h]
        for i in eye_indices
    ], dtype=np.float64)

    # Vertical distances
    A = np.linalg.norm(pts[1] - pts[5])
    B = np.linalg.norm(pts[2] - pts[4])
    # Horizontal distance
    C = np.linalg.norm(pts[0] - pts[3])
    return (A + B) / (2.0 * C + 1e-6)


class BlinkMonitor:
    """Track blink rate and flag abnormal patterns."""

    def __init__(self, logger: ViolationLogger):
        self.logger = logger

        # Blink tracking
        self._closed_frames  = 0
        self._blink_times    = deque()   # Timestamps of each blink
        self._last_event_time = 0.0
        self._started_at      = time.time()
        self._ear_samples     = deque(maxlen=240)
        self._dynamic_threshold = EAR_THRESHOLD
        self._abnormal_streak  = 0
        self._baseline_ready   = False

        # Public state (read by HUD)
        self.blink_count     = 0
        self.blinks_per_min  = 0.0
        self.current_ear     = 1.0
        self.status          = "NORMAL"

        print("[BlinkMonitor] Initialised (EAR-based blink detection).")

    # ── Public ────────────────────────────────────────────────────────────────

    def process(self, landmarks, frame_bgr, annotated_bgr, frame_index: int, w: int, h: int) -> dict:
        """
        Called each frame with the face landmarks from GazeTracker.
        landmarks: list of NormalizedLandmark from MediaPipe FaceLandmarker.
        """
        if not landmarks:
            return {"blink_rate": self.blinks_per_min, "status": self.status}

        left_ear  = _ear(landmarks, LEFT_EYE_IDX,  w, h)
        right_ear = _ear(landmarks, RIGHT_EYE_IDX, w, h)
        ear       = (left_ear + right_ear) / 2.0
        self.current_ear = round(ear, 3)
        self._update_baseline(left_ear, right_ear, ear)

        # Detect blink
        if self._is_eye_closed(left_ear, right_ear, ear):
            self._closed_frames += 1
        else:
            if self._closed_frames >= EAR_CONSEC_FRAMES:
                self._register_blink(frame_bgr, frame_index)
            self._closed_frames = 0

        self._update_rate()
        self._check_violation(frame_bgr, frame_index)
        self._draw_info(annotated_bgr, ear)

        return {
            "blink_rate": self.blinks_per_min,
            "blink_count": self.blink_count,
            "ear": self.current_ear,
            "status": self.status,
            "threshold": round(self._dynamic_threshold, 3),
            "anomaly": self.status != "NORMAL" and self._abnormal_streak >= ANOMALY_STREAK_REQ and self.blinks_per_min > 0.0,
        }

    # ── Private ───────────────────────────────────────────────────────────────

    def _register_blink(self, frame, frame_index):
        now = time.time()
        self.blink_count += 1
        self._blink_times.append(now)

    def _update_baseline(self, left_ear, right_ear, ear):
        now = time.time()
        if abs(left_ear - right_ear) < 0.08 and ear > EAR_THRESHOLD:
            self._ear_samples.append(ear)
        if now - self._started_at >= BASELINE_SEC and self._ear_samples:
            baseline = float(np.percentile(self._ear_samples, 65))
            self._dynamic_threshold = max(0.14, min(EAR_THRESHOLD, baseline * 0.72))
            self._baseline_ready = True

    def _is_eye_closed(self, left_ear, right_ear, ear) -> bool:
        threshold = self._dynamic_threshold if self._baseline_ready else EAR_THRESHOLD
        # Glasses glare often corrupts only one eye. Require both eyes to be consistently low.
        return (
            ear < threshold and
            max(left_ear, right_ear) < threshold * 1.12 and
            abs(left_ear - right_ear) < 0.09
        )

    def _update_rate(self):
        now = time.time()
        # Prune blinks outside the rolling window
        while self._blink_times and now - self._blink_times[0] > MEASURE_WINDOW_SEC:
            self._blink_times.popleft()

        window_elapsed = min(now - (self._blink_times[0] if self._blink_times else now),
                             MEASURE_WINDOW_SEC)
        observation_elapsed = now - self._started_at
        if observation_elapsed >= MIN_OBSERVATION_SEC and window_elapsed > 5.0:
            self.blinks_per_min = round(len(self._blink_times) / window_elapsed * 60.0, 1)
        else:
            self.blinks_per_min = 0.0

    def _check_violation(self, frame, frame_index):
        now = time.time()
        bpm = self.blinks_per_min

        if bpm == 0.0:
            self.status = "CALIBRATING" if not self._baseline_ready else "NORMAL"
            return   # Not enough data

        # Moderate: only flag if outside normal range
        if now - self._started_at < LOW_RATE_GRACE_SEC:
            low_blink = False
        else:
            low_blink = bpm < LOW_BLINK_THRESHOLD

        if low_blink:
            self.status = "LOW_BLINK"
        elif bpm > HIGH_BLINK_THRESHOLD:
            self.status = "HIGH_BLINK"
        else:
            self.status = "NORMAL"
            self._abnormal_streak = 0
            return

        self._abnormal_streak += 1
        if self._abnormal_streak < ANOMALY_STREAK_REQ:
            return

        if now - self._last_event_time < EVENT_COOLDOWN_SEC:
            return

        path = capture_screenshot(frame, frame_index, "blink_rate")
        self.logger.log(
            violation_type  = ViolationType.BLINK_ANOMALY,
            confidence      = 0.75,
            screenshot_path = path,
            extra           = {
                "blinks_per_min": bpm,
                "status":         self.status,
                "note": (
                    "Very low blink rate — possible reading from notes"
                    if self.status == "LOW_BLINK" else
                    "Very high blink rate — possible stress/cheating"
                ),
            },
        )
        self._last_event_time = now

    def _draw_info(self, annotated, ear):
        color = (0, 220, 80) if self.status == "NORMAL" else (0, 100, 255)
        lines = [
            f"EAR: {ear:.3f}",
            f"Blinks: {self.blink_count}",
            f"BPM: {self.blinks_per_min:.1f}",
            f"Thr: {self._dynamic_threshold:.3f}",
            f"Eye: {self.status}",
        ]
        x = annotated.shape[1] - 260
        for i, line in enumerate(lines):
            cv2.putText(
                annotated, line, (x, 110 + i * 22),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 1, cv2.LINE_AA,
            )
