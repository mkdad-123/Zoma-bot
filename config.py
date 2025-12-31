import numpy as np

# ==============================
# Configuration & Constants
# ==============================

HSV_GREEN_LOWER = np.array([35, 40, 40])
HSV_GREEN_UPPER = np.array([85, 255, 255])

MIN_GAME_AREA_SIZE = 300

PREVIEW_SCALE_PERCENT = 60

EXCLUDED_TOP_LEFT = (150, 180)
EXCLUDED_TOP_RIGHT_MARGIN = 150

COLOR_DRAW_MAP = {
    "Red": (0, 0, 255),
    "Green": (0, 255, 0),
    "Blue": (255, 0, 0),
    "Yellow": (0, 255, 255),
    "Purple": (255, 0, 255),
}

FROG_CENTER = (417, 348)
FROG_RADIUS = 80
