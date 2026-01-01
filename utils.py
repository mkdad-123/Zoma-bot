import cv2
import time

def set_window():
    window_name = "Zuma Bot Preview"
    cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_TOPMOST, 1)
    cv2.moveWindow(window_name, 10, 10)
    return window_name

def resize_widow(annotated, scale):
    resized = cv2.resize(
                annotated,
                None,
                fx=scale,
                fy=scale,
                interpolation=cv2.INTER_AREA
            )
    
    return resized

def show_fps(last_time, annotated):
    now = time.time()
    fps = 1 / (now - last_time)
    cv2.putText(annotated, f"FPS: {int(fps)}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    return now

def crop_around_center(frame, center, size):
    """
    Crops a square ROI around a given center.

    center: (cx, cy)
    size: side length of square
    """
    h, w = frame.shape[:2]
    cx, cy = center
    half = size // 2

    x1 = max(cx - half, 0)
    y1 = max(cy - half, 0)
    x2 = min(cx + half, w)
    y2 = min(cy + half, h)

    roi = frame[y1:y2, x1:x2]
    return roi, (x1, y1)
