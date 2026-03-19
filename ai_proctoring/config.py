"""
Centralised Configuration
Edit this file to tune the entire proctoring system.
No need to touch individual module files.
"""

import os

MODULE_DIR = os.path.dirname(os.path.abspath(__file__))

# ── Session ────────────────────────────────────────────────────────────────────
CANDIDATE_ID    = "CANDIDATE-001"
EXAM_NAME       = "General Examination"
INSTITUTION     = "Your Institution"

# ── Camera ─────────────────────────────────────────────────────────────────────
WEBCAM_INDEX    = 0
FRAME_WIDTH     = 1280
FRAME_HEIGHT    = 720
TARGET_FPS      = 30
SHOW_PREVIEW    = False
SHOW_DEBUG_INFO = True

# ── Strictness preset ──────────────────────────────────────────────────────────
# "strict"   → flag immediately, low thresholds
# "moderate" → allow minor violations, flag repeated/sustained ones  ← DEFAULT
# "lenient"  → high thresholds, only obvious cheating
STRICTNESS = "moderate"

_PRESETS = {
    "strict": dict(
        NO_FACE_TIMEOUT_SEC       = 2.0,
        LOOK_AWAY_TIMEOUT_SEC     = 1.5,
        TALKING_SEC               = 1.0,
        AUDIO_SUSTAINED_SEC       = 0.5,
        AUDIO_SPIKE_LIMIT         = 2,
        SWITCH_LIMIT              = 1,
        MOTION_AREA_PCT           = 0.05,
        SIMILARITY_THRESH         = 0.82,
    ),
    "moderate": dict(
        NO_FACE_TIMEOUT_SEC       = 5.0,
        LOOK_AWAY_TIMEOUT_SEC     = 3.0,
        TALKING_SEC               = 3.0,
        AUDIO_SUSTAINED_SEC       = 2.0,
        AUDIO_SPIKE_LIMIT         = 3,
        SWITCH_LIMIT              = 2,
        MOTION_AREA_PCT           = 0.08,
        SIMILARITY_THRESH         = 0.75,
    ),
    "lenient": dict(
        NO_FACE_TIMEOUT_SEC       = 10.0,
        LOOK_AWAY_TIMEOUT_SEC     = 6.0,
        TALKING_SEC               = 6.0,
        AUDIO_SUSTAINED_SEC       = 4.0,
        AUDIO_SPIKE_LIMIT         = 5,
        SWITCH_LIMIT              = 4,
        MOTION_AREA_PCT           = 0.15,
        SIMILARITY_THRESH         = 0.65,
    ),
}

if STRICTNESS not in _PRESETS:
    raise ValueError(f"Unsupported STRICTNESS '{STRICTNESS}'. Choose from: {', '.join(_PRESETS)}")

# Merge selected preset into module-level names
_preset = _PRESETS[STRICTNESS]
NO_FACE_TIMEOUT_SEC   = _preset["NO_FACE_TIMEOUT_SEC"]
LOOK_AWAY_TIMEOUT_SEC = _preset["LOOK_AWAY_TIMEOUT_SEC"]
TALKING_SEC           = _preset["TALKING_SEC"]
AUDIO_SUSTAINED_SEC   = _preset["AUDIO_SUSTAINED_SEC"]
AUDIO_SPIKE_LIMIT     = _preset["AUDIO_SPIKE_LIMIT"]
SWITCH_LIMIT          = _preset["SWITCH_LIMIT"]
MOTION_AREA_PCT       = _preset["MOTION_AREA_PCT"]
SIMILARITY_THRESH     = _preset["SIMILARITY_THRESH"]

# ── Feature toggles ────────────────────────────────────────────────────────────
ENABLE_FACE_MONITOR    = True
ENABLE_GAZE_TRACKING   = True
ENABLE_PHONE_DETECTION = True
ENABLE_OBJECT_DETECT   = True
ENABLE_AUDIO_MONITOR   = True
ENABLE_BLINK_MONITOR   = True
ENABLE_LIP_MONITOR     = True
ENABLE_TAB_MONITOR     = True
ENABLE_LIGHTING_MONITOR= True
ENABLE_MOTION_DETECT   = True
ENABLE_IDENTITY_VERIFY = True

# ── Output ─────────────────────────────────────────────────────────────────────
SCREENSHOTS_DIR        = os.path.join(MODULE_DIR, "screenshots")
LOG_FILE               = os.path.join(MODULE_DIR, "violations.jsonl")
YOLO_MODEL             = os.path.join(MODULE_DIR, "yolov8n.pt")     # swap yolov8s.pt for more accuracy

# ── Head pose thresholds ───────────────────────────────────────────────────────
YAW_THRESHOLD_DEG        = 25.0
PITCH_UP_THRESHOLD_DEG   = 20.0
PITCH_DOWN_THRESHOLD_DEG = 40.0   # Down is allowed (writing)

# ── Blink rate ─────────────────────────────────────────────────────────────────
LOW_BLINK_THRESHOLD  = 3    # blinks/min
HIGH_BLINK_THRESHOLD = 40   # blinks/min

# Shared detector tuning
FACE_MIN_DETECTION_CONF    = 0.6
FACE_MULTI_FACE_COOLDOWN   = 3.0
GAZE_EVENT_COOLDOWN_SEC    = 5.0
GAZE_AWAY_FRAME_STREAK     = 4
PHONE_CONF_THRESH          = 0.45
PHONE_STREAK_FRAMES        = 2
PHONE_EVENT_COOLDOWN_SEC   = 4.0
OBJECT_CONF_THRESH         = 0.35
OBJECT_EVENT_COOLDOWN_SEC  = 5.0
BLINK_EAR_THRESHOLD        = 0.18
BLINK_EAR_CONSEC_FRAMES    = 3
BLINK_MIN_OBSERVATION_SEC  = 45.0
BLINK_LOW_RATE_GRACE_SEC   = 90.0
BLINK_RATE_ANOMALY_STREAK  = 3
BLINK_BASELINE_SEC         = 12.0
BLINK_EVENT_COOLDOWN_SEC   = 45.0
LIP_MAR_THRESHOLD          = 0.05
LIP_MOVEMENT_STD_THRESHOLD = 0.0045
LIP_EVENT_COOLDOWN_SEC     = 8.0
LIP_MIN_TALKING_CYCLES     = 6
LIGHT_HISTORY_LEN          = 60
LIGHT_SPIKE_DELTA          = 40
LIGHT_DARK_THRESHOLD       = 25
LIGHT_DARK_DURATION_SEC    = 3.0
LIGHT_EVENT_COOLDOWN_SEC   = 8.0
MOTION_THRESH              = 25
MOTION_SUSTAINED_SEC       = 2.0
MOTION_EVENT_COOLDOWN_SEC  = 8.0
IDENTITY_ENROLL_FRAMES     = 30
IDENTITY_CHECK_INTERVAL    = 10.0
IDENTITY_EVENT_COOLDOWN    = 20.0
IDENTITY_MISMATCH_STREAK   = 2

# Audio tuning
AUDIO_ABS_THRESHOLD        = 2200
AUDIO_BASELINE_ALPHA       = 0.08
AUDIO_TRIGGER_MULTIPLIER   = 3.0
AUDIO_MIN_TRIGGER_RMS      = 2500
AUDIO_SPIKE_WINDOW_SEC     = 12.0
AUDIO_SPIKE_MIN_GAP_SEC    = 1.2
AUDIO_EVENT_COOLDOWN_SEC   = 10.0
AUDIO_CALIBRATION_SEC      = 4.0
AUDIO_SMOOTHING_ALPHA      = 0.2
