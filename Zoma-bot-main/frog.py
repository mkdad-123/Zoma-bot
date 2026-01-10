import cv2
import numpy as np
from config import *
from utils import crop_around_center


def get_frog_balls_by_color(frame):

    roi, (x_offset, y_offset) = crop_around_center(
        frame, BACK_BALL_CENTER, FROG_RADIUS * 2
    )

    hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    found = []

    for color_name in COLOR_DRAW_MAP.keys():
        mask = get_color_mask(hsv_roi, color_name)

        kernel = np.ones((7, 7), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        contours, _ = cv2.findContours(
            mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < BALL_MIN_AREA or area > 2000:
                continue

            peri = cv2.arcLength(cnt, True)
            if peri == 0:
                continue

            circ = 4 * np.pi * area / (peri * peri)
            if circ < 0.45:
                continue

            M = cv2.moments(cnt)
            if M["m00"] == 0:
                continue

            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])

            dist = np.linalg.norm(
                np.array([cx, cy]) - np.array([FROG_RADIUS, FROG_RADIUS])
            )

            found.append({
                "color": color_name,
                "pos_in_roi": (cx, cy),
                "abs_pos": (cx + x_offset, cy + y_offset),
                "dist": dist
            })

    if not found:
        return None, None, (x_offset, y_offset, FROG_RADIUS * 2)

    found.sort(key=lambda x: x["dist"])
    back_ball = found[0]
    mouth_ball = found[1] if len(found) > 1 else None

    return back_ball, mouth_ball, (x_offset, y_offset, FROG_RADIUS * 2)


def get_color_mask(hsv, color):

    if color == "Green":
        return cv2.inRange(hsv, (50, 120, 125), (75, 255, 255))
    if color == "Blue":
        return cv2.inRange(hsv, (100, 110, 120), (130, 255, 255))
    if color == "Yellow":
        return cv2.inRange(hsv, (20, 150, 120), (35, 255, 255))
    if color == "Purple":
        return cv2.inRange(hsv, (135, 110, 120), (158, 255, 255))

    return np.zeros(hsv.shape[:2], dtype=np.uint8)
