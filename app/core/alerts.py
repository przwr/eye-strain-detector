"""Out-of-window alerts: sound + desktop notifications."""
import os
import shutil
import subprocess
import sys
import threading
import time

try:
    from plyer import notification as _plyer_notification
except Exception:
    _plyer_notification = None


def _beep_blocking(freq, dur_ms):
    if sys.platform.startswith("win"):
        try:
            import winsound
            winsound.Beep(freq, dur_ms)
            return
        except Exception:
            pass
    elif sys.platform == "darwin":
        if os.system("afplay /System/Library/Sounds/Sosumi.aiff >/dev/null 2>&1") == 0:
            return
    elif shutil.which("paplay"):
        # shortcut: fixed freedesktop sound, no volume/repeat control
        if os.system("paplay /usr/share/sounds/freedesktop/stereo/alarm-clock-elapsed.oga >/dev/null 2>&1") == 0:
            return
    print("\a", end="", flush=True)


def beep(freq=1000, dur_ms=350):
    return  # sound disabled by user; popups remain (re-enable: delete this line)
    threading.Thread(target=_beep_blocking, args=(freq, dur_ms), daemon=True).start()


def notify(title, message):
    # plyer isn't installed (missing from requirements.txt) and its Linux
    # backend needs dbus-python anyway; notify-send is the working path here.
    if shutil.which("notify-send"):
        def _run_send():
            try:
                subprocess.run(["notify-send", "-a", "Iris", "-t", "5000", title, message],
                               timeout=5, check=False)
            except Exception:
                pass
        threading.Thread(target=_run_send, daemon=True).start()
        return
    if _plyer_notification is None:
        return
    def _run():
        try:
            _plyer_notification.notify(title=title, message=message,
                                       app_name="Eye Strain Detector", timeout=5)
        except Exception:
            pass
    threading.Thread(target=_run, daemon=True).start()


class AlertManager:
    def __init__(self, proximity_cooldown=8.0, strain_cooldown=30.0,
                 proximity_sustain_sec=10.0):
        self.proximity_cooldown = proximity_cooldown
        self.strain_cooldown = strain_cooldown
        # momentary leans / sitting down must not alert: require sustained closeness
        self.proximity_sustain_sec = proximity_sustain_sec
        self._last_prox = 0.0
        self._last_strain = 0.0
        self._prev_strain = "low"
        self._too_close_since: float | None = None

    def update(self, *, proximity, strain, face_detected, ts=None):
        ts = time.time() if ts is None else ts
        if not face_detected:
            self._prev_strain = strain
            return
        if proximity == "TOO CLOSE":
            if self._too_close_since is None:
                self._too_close_since = ts
        else:
            self._too_close_since = None
        sustained = (
            self._too_close_since is not None
            and ts - self._too_close_since >= self.proximity_sustain_sec
        )
        if sustained and ts - self._last_prox >= self.proximity_cooldown:
            beep(900, 250)
            notify("Move back from screen", "You're sitting too close to the display.")
            self._last_prox = ts
        if strain == "high":
            worsened = self._prev_strain != "high"
            if worsened or ts - self._last_strain >= self.strain_cooldown:
                beep(1200, 500)
                notify("Time for a break",
                       "High eye strain detected. Try the 20-20-20 rule: look 20 ft away for 20 seconds.")
                self._last_strain = ts
        self._prev_strain = strain
