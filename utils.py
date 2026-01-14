import math
import cv2
import time


# ==============================
# Window utils
# ==============================
def set_window():
    window_name = "Zuma Bot Preview"
    cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_TOPMOST, 1)
    cv2.moveWindow(window_name, 10, 10)
    return window_name


def resize_widow(annotated, scale):
    return cv2.resize(
        annotated,
        None,
        fx=scale,
        fy=scale,
        interpolation=cv2.INTER_AREA
    )


# ==============================
# FPS (واحدة فقط ✔️)
# ==============================
def show_fps(last_time, frame):
    now = time.time()
    fps = 1 / max(now - last_time, 1e-6)

    # الحصول على أبعاد النافذة (الارتفاع والعرض)
    h, w = frame.shape[:2]

    # الإحداثيات: (10 بكسل من اليسار، الارتفاع الكلي - 20 بكسل من الأسفل)
    position = (10, h - 20)

    cv2.putText(
        frame,
        f"FPS: {int(fps)}",
        position,
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,         # صغرنا الحجم قليلاً ليكون أنيقاً في الأسفل
        (0, 255, 255), # اللون الأصفر (BGR: 0 Blue, 255 Green, 255 Red)
        2
    )
    return now


# ==============================
# Image helpers
# ==============================
def crop_around_center(frame, center, size):
    h, w = frame.shape[:2]
    cx, cy = center
    half = size // 2

    x1 = max(cx - half, 0)
    y1 = max(cy - half, 0)
    x2 = min(cx + half, w)
    y2 = min(cy + half, h)

    roi = frame[y1:y2, x1:x2]
    return roi, (x1, y1)


# ==============================
# AIM
# ==============================
def compute_angle(shooter_center, target_pos):
    dx = target_pos[0] - shooter_center[0]
    dy = target_pos[1] - shooter_center[1]
    return math.degrees(math.atan2(dy, dx))
