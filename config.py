import numpy as np

# ==============================
# Configuration & Constants
# config.py
# ==============================

HSV_GREEN_LOWER = np.array([35, 40, 40])
HSV_GREEN_UPPER = np.array([85, 255, 255])

MIN_GAME_AREA_SIZE = 300
PREVIEW_SCALE_PERCENT = 68

EXCLUDED_TOP_LEFT = (150, 180)
EXCLUDED_TOP_RIGHT_MARGIN = 150

COLOR_DRAW_MAP = {
    "Red": (0, 0, 255),
    "Green": (0, 255, 0),
    "Blue": (255, 0, 0),
    "Yellow": (0, 255, 255),
    "Purple": (255, 0, 255),
    "Orange": (0, 165, 255)
}

BACK_BALL_CENTER = (417, 348)
FROG_RADIUS = 110
BALL_MIN_AREA = 75

# ===============================
# Zuma HTML5 Path Color (HSV)
# ===============================
PATH_HSV_LOW = (35, 40, 40)
PATH_HSV_HIGH = (85, 255, 255)
# ===============================
# UI Overlay Mask (Top Right)
# ===============================
# ==========================
# UI MASK (Top bar exclusion)
# ==========================
# ==========================
# UI MASK (Top Bar)
# ==========================
UI_MASK_TOP = {
    "height": 80   # عدّلي الرقم إذا لزم (60–100 حسب الدقة)
}
