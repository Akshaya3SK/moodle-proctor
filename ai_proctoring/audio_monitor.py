"""
Audio Monitor Module
Listens to the microphone in a background thread.
Flags suspicious sounds (talking, loud noise) that persist beyond a threshold.

Moderate mode:
  - Single short sound  → warning only
  - Sustained sound > 2 s OR 3+ spikes in 10 s → violation
"""

import time
import threading
import numpy as np
from collections import deque

import config as C
from violation_logger import ViolationLogger, ViolationType


# ─── Tuning ───────────────────────────────────────────────────────────────────
SAMPLE_RATE        = 16000
CHUNK_SIZE         = 1024
SOUND_THRESHOLD    = C.AUDIO_ABS_THRESHOLD
SUSTAINED_SEC      = C.AUDIO_SUSTAINED_SEC
SPIKE_WINDOW_SEC   = C.AUDIO_SPIKE_WINDOW_SEC
SPIKE_COUNT_LIMIT  = C.AUDIO_SPIKE_LIMIT
SPIKE_MIN_GAP_SEC  = C.AUDIO_SPIKE_MIN_GAP_SEC
EVENT_COOLDOWN_SEC = C.AUDIO_EVENT_COOLDOWN_SEC
CALIBRATION_SEC    = C.AUDIO_CALIBRATION_SEC
BASELINE_ALPHA     = C.AUDIO_BASELINE_ALPHA
TRIGGER_MULTIPLIER = C.AUDIO_TRIGGER_MULTIPLIER
MIN_TRIGGER_RMS    = C.AUDIO_MIN_TRIGGER_RMS
SMOOTHING_ALPHA    = C.AUDIO_SMOOTHING_ALPHA


class AudioMonitor:
    """Background microphone monitor."""

    def __init__(self, logger: ViolationLogger):
        self.logger   = logger
        self._running = False
        self._thread  = None
        self._stream  = None
        self._pa      = None

        # State
        self._sound_start     = None
        self._spike_times     = deque()
        self._last_event_time = 0.0
        self._last_spike_time = 0.0
        self._was_loud        = False
        self._started_at      = time.time()
        self._baseline_rms    = 0.0
        self._smoothed_rms    = 0.0
        self.current_rms      = 0
        self.status           = "CALIBRATING"

        self._try_start()

    # ── Public ────────────────────────────────────────────────────────────────

    def stop(self):
        self._running = False
        if self._stream:
            try:
                self._stream.stop_stream()
                self._stream.close()
            except Exception:
                pass
        if self._pa:
            try:
                self._pa.terminate()
            except Exception:
                pass
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)

    # ── Private ───────────────────────────────────────────────────────────────

    def _try_start(self):
        try:
            import pyaudio
            self._pa     = pyaudio.PyAudio()
            self._stream = self._pa.open(
                format            = pyaudio.paInt16,
                channels          = 1,
                rate              = SAMPLE_RATE,
                input             = True,
                frames_per_buffer = CHUNK_SIZE,
            )
            self._running = True
            self._thread  = threading.Thread(target=self._listen_loop, daemon=True)
            self._thread.start()
            print("[AudioMonitor] Microphone monitoring started.")
        except ImportError:
            print("[AudioMonitor] WARNING: pyaudio not installed. "
                  "Run: pip install pyaudio")
        except Exception as exc:
            print(f"[AudioMonitor] WARNING: Cannot open microphone — {exc}")

    def _listen_loop(self):
        while self._running:
            try:
                raw  = self._stream.read(CHUNK_SIZE, exception_on_overflow=False)
                data = np.frombuffer(raw, dtype=np.int16).astype(np.float32)
                rms  = float(np.sqrt(np.mean(data ** 2)))
                self._smoothed_rms = (
                    rms if self._smoothed_rms == 0.0
                    else (SMOOTHING_ALPHA * rms + (1.0 - SMOOTHING_ALPHA) * self._smoothed_rms)
                )
                self.current_rms = int(self._smoothed_rms)
                self._evaluate(self._smoothed_rms)
            except Exception:
                time.sleep(0.05)

    def _evaluate(self, rms: float):
        now   = time.time()
        self._update_baseline(rms, now)
        trigger_threshold = max(SOUND_THRESHOLD, self._baseline_rms * TRIGGER_MULTIPLIER, MIN_TRIGGER_RMS)
        loud  = rms > trigger_threshold

        if loud:
            self.status = "SOUND_DETECTED"
            if not self._was_loud and now - self._last_spike_time >= SPIKE_MIN_GAP_SEC:
                self._spike_times.append(now)
                self._last_spike_time = now
            while self._spike_times and now - self._spike_times[0] > SPIKE_WINDOW_SEC:
                self._spike_times.popleft()

            if self._sound_start is None:
                self._sound_start = now

            elapsed = now - self._sound_start

            # Violation condition (moderate): sustained OR repeated spikes
            sustained_viol = elapsed >= SUSTAINED_SEC
            spike_viol     = len(self._spike_times) >= SPIKE_COUNT_LIMIT

            if (sustained_viol or spike_viol) and (now - self._last_event_time >= EVENT_COOLDOWN_SEC):
                reason = "sustained_sound" if sustained_viol else "repeated_spikes"
                self.logger.log(
                    violation_type  = ViolationType.AUDIO_VIOLATION,
                    confidence      = min(1.0, rms / (SOUND_THRESHOLD * 2)),
                    screenshot_path = "N/A (audio event)",
                    extra           = {
                        "reason":       reason,
                        "rms":          self.current_rms,
                        "baseline_rms": int(self._baseline_rms),
                        "threshold":    int(trigger_threshold),
                        "spike_count":  len(self._spike_times),
                        "elapsed_sec":  round(elapsed, 2),
                    },
                )
                self._last_event_time = now
                self._sound_start     = None
                self._spike_times.clear()
            self._was_loud = True
        else:
            self.status       = "QUIET"
            self._sound_start = None
            self._was_loud    = False

    def _update_baseline(self, rms: float, now: float):
        if self._baseline_rms == 0.0:
            self._baseline_rms = rms
            return
        # During calibration or quiet periods, adapt to room noise gradually.
        if now - self._started_at < CALIBRATION_SEC or rms < max(SOUND_THRESHOLD, self._baseline_rms * 1.6):
            self._baseline_rms = (
                BASELINE_ALPHA * rms +
                (1.0 - BASELINE_ALPHA) * self._baseline_rms
            )
        if now - self._started_at < CALIBRATION_SEC:
            self.status = "CALIBRATING"
