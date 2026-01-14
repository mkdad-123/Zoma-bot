import cv2
import numpy as np
from config import *
from utils import crop_around_center

# ==============================
# Game Window Detection
# ==============================

def detect_game_window(frame):
    """
    Detects the Zuma game window using green background segmentation.
    Returns (x, y, w, h) or None.
    """
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, HSV_GREEN_LOWER, HSV_GREEN_UPPER)

    contours, _ = cv2.findContours(
        mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    if not contours:
        return None

    largest = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(largest)

    if w > MIN_GAME_AREA_SIZE and h > MIN_GAME_AREA_SIZE:
        return x, y, w, h

    return None

# ==============================
# Color Classification
# ==============================

def classify_ball_color(hsv_pixel):
    """
    Rule-based color classification for Zuma balls.
    Returns color name or None.
    """
    h, s, v = hsv_pixel

    # Brightness & saturation filtering
    if s < 120 or v < 120:
        return None

    if h <= 10 or h >= 160:
        return "Red"

    if 40 <= h <= 90 and s > 150 and v > 180:
        return "Green"

    if 100 <= h <= 130 and s > 110:
        return "Blue"

    if 20 <= h <= 35 and s > 150:
        return "Yellow"

    if 135 <= h <= 158 and s > 110:
        return "Purple"

    return None


# ==============================
# Ball Detection
# ==============================

def detect_balls(frame):
    """
    Detects Zuma balls using HoughCircles + color validation.
    Returns annotated frame and list of detected balls.
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (7, 7), 2)

    circles = cv2.HoughCircles(
        blurred,
        cv2.HOUGH_GRADIENT,
        dp=1.2,
        minDist=30,
        param1=50,
        param2=25,
        minRadius=15,
        maxRadius=25
    )

    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    detected_balls = []

    if circles is None:
        return frame, detected_balls

    circles = np.around(circles).astype(int)
    

    for cx, cy, r in circles[0]:
        
        # Exclude static background regions
        if cx < EXCLUDED_TOP_LEFT[0] and cy < EXCLUDED_TOP_LEFT[1]:
            continue

        if cx > (frame.shape[1] - EXCLUDED_TOP_RIGHT_MARGIN) and cy < 150:
            continue
        
        h, w = hsv_frame.shape[:2]

        if cx < 0 or cy < 0 or cx >= w or cy >= h:
            continue

        avg = sample_hsv_roi(hsv_frame, cx, cy)
        if avg is None:
            continue

        color = classify_ball_color(avg)
        if color is None:
            continue

        draw_color = COLOR_DRAW_MAP[color]
        cv2.circle(frame, (cx, cy), r, draw_color, 2)
        text_x = max(cx - 15, 0)
        text_y = max(cy - 25, 0)

        cv2.putText(
            frame, color, (text_x, text_y),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, draw_color, 1
        )

        detected_balls.append({
            "pos": (cx, cy),
            "color": color
        })

    return frame, detected_balls


def sample_hsv_roi(hsv_frame, cx, cy):

    h, w = hsv_frame.shape[:2]

    x1 = max(cx - 5, 0)
    y1 = max(cy - 5, 0)
    x2 = min(cx + 5, w)
    y2 = min(cy + 5, h)

    roi = hsv_frame[y1:y2, x1:x2]
    if roi.size == 0:
        return None
    avg = cv2.mean(roi)[:3]
    

    return avg




