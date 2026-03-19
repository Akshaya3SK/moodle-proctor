"""
Lip Movement Monitor
Analyses the mouth aspect ratio (MAR) from FaceMesh landmarks to detect
sustained talking or whispering — a strong indicator of cheating.

Moderate mode: flags only after lips move continuously for > 3 seconds.
"""

import cv2
import time
import numpy as np
from collections import deque

import config as C
from violation_logger import ViolationLogger, ViolationType
from utils import capture_screenshot


# MediaPipe FaceLandmarker mouth landmark indices
# Upper lip: 13, Lower lip: 14, Left corner: 78, Right corner: 308
MOUTH_TOP    = 13
MOUTH_BOTTOM = 14
MOUTH_LEFT   = 78
MOUTH_RIGHT  = 308

MAR_THRESHOLD      = C.LIP_MAR_THRESHOLD
TALKING_SEC        = C.TALKING_SEC
EVENT_COOLDOWN_SEC = C.LIP_EVENT_COOLDOWN_SEC
MOVEMENT_STD_THRESH = C.LIP_MOVEMENT_STD_THRESHOLD
MIN_TALKING_CYCLES = C.LIP_MIN_TALKING_CYCLES
HISTORY_LEN        = 30     # Frames of MAR history for smoothing


class LipMovementMonitor:
    """Detect sustained lip/mouth movement (talking, whispering)."""

    def __init__(self, logger: ViolationLogger):
        self.logger          = logger
        self._talk_start     = None
        self._last_event_time = 0.0
        self._mar_history    = deque(maxlen=HISTORY_LEN)
        self._movement_cycles = 0
        self._prev_delta_sign = 0
        self.current_mar     = 0.0
        self.status          = "CLOSED"
        print("[LipMonitor] Initialised (MAR-based lip movement detection).")

    def process(self, landmarks, frame_bgr, annotated_bgr, frame_index, w, h) -> dict:
        if not landmarks:
            return {"lip_status": "NO_FACE", "mar": 0.0}

        mar = self._compute_mar(landmarks, w, h)
        self._mar_history.append(mar)
        smooth_mar       = float(np.mean(self._mar_history))
        mar_std          = float(np.std(self._mar_history)) if len(self._mar_history) > 3 else 0.0
        self.current_mar = round(smooth_mar, 4)
        self._update_movement_cycles()

        mouth_open = smooth_mar > MAR_THRESHOLD
        talking = mouth_open and mar_std >= MOVEMENT_STD_THRESH and self._movement_cycles >= MIN_TALKING_CYCLES
        self.status = "talking" if talking else ("open" if mouth_open else "closed")

        self._handle_talking(talking, frame_bgr, annotated_bgr, frame_index, smooth_mar)
        self._draw_info(annotated_bgr, smooth_mar, talking)

        return {"lip_status": self.status, "mar": self.current_mar, "talking": talking}

    def _compute_mar(self, landmarks, w, h) -> float:
        def pt(idx):
            return np.array([landmarks[idx].x * w, landmarks[idx].y * h])

        top    = pt(MOUTH_TOP)
        bottom = pt(MOUTH_BOTTOM)
        left   = pt(MOUTH_LEFT)
        right  = pt(MOUTH_RIGHT)

        vertical   = np.linalg.norm(top - bottom)
        horizontal = np.linalg.norm(left - right) + 1e-6
        return vertical / horizontal

    def _update_movement_cycles(self):
        if len(self._mar_history) < 4:
            return
        recent = list(self._mar_history)[-4:]
        delta = recent[-1] - recent[-2]
        sign = 1 if delta > 0.001 else -1 if delta < -0.001 else 0
        if sign != 0 and self._prev_delta_sign != 0 and sign != self._prev_delta_sign:
            self._movement_cycles += 1
        self._prev_delta_sign = sign
        if len(self._mar_history) == self._mar_history.maxlen and np.std(self._mar_history) < MOVEMENT_STD_THRESH * 0.5:
            self._movement_cycles = 0

    def _handle_talking(self, mouth_open, frame, annotated, frame_index, mar):
        now = time.time()
        if mouth_open:
            if self._talk_start is None:
                self._talk_start = now
            elapsed   = now - self._talk_start
            remaining = max(0.0, TALKING_SEC - elapsed)
            cv2.putText(annotated,
                        f"LIP MOVEMENT — violation in {remaining:.1f}s",
                        (20, 225), cv2.FONT_HERSHEY_SIMPLEX, 0.75,
                        (0, 80, 255), 2, cv2.LINE_AA)

            if elapsed >= TALKING_SEC and now - self._last_event_time >= EVENT_COOLDOWN_SEC:
                path = capture_screenshot(frame, frame_index, "talking")
                self.logger.log(
                    violation_type  = ViolationType.TALKING_DETECTED,
                    confidence      = min(1.0, mar / (MAR_THRESHOLD * 3)),
                    screenshot_path = path,
                    extra           = {"mar": round(mar, 4),
                                       "elapsed_sec": round(elapsed, 2)},
                )
                self._last_event_time = now
                self._talk_start      = None
        else:
            self._talk_start = None

    def _draw_info(self, annotated, mar, mouth_open):
        color = (0, 80, 255) if mouth_open else (0, 220, 80)
        cv2.putText(annotated,
                    f"Mouth: {'OPEN' if mouth_open else 'CLOSED'}  MAR:{mar:.3f}",
                    (annotated.shape[1]-300, 200),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 1, cv2.LINE_AA)
