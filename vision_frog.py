import cv2
import numpy as np
from config import *
from utils import crop_around_center

def get_frog_balls_by_color(frame):
  
    roi, (x_offset, y_offset) = crop_around_center(frame, BACK_BALL_CENTER, FROG_RADIUS * 2)
    hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    
    found_colors = []

    for color_name, bgr_color in COLOR_DRAW_MAP.items():
        mask = get_color_mask(hsv_roi, color_name)

        if color_name == "Green" or color_name == "Yellow" :
            debug_mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
            cv2.putText(debug_mask, f"{color_name} Mask", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
            debug_mask = cv2.resize(debug_mask, None, fx=2, fy=2)
            cv2.imshow(f"{color_name} Mask Debug", debug_mask)
        

        kernel = np.ones((7,7), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        
        
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > 2000:
                continue 
            
            if  area > BALL_MIN_AREA : 
                perimeter = cv2.arcLength(cnt, True)
                circularity = 4 * np.pi * (area / (perimeter * perimeter)) if perimeter > 0 else 0
                
                if circularity > 0.45:
                    M = cv2.moments(cnt)
                    if M["m00"] != 0:
                        cx = int(M["m10"] / M["m00"])
                        cy = int(M["m01"] / M["m00"])
                        
                        found_colors.append({
                            "color": color_name,
                            "pos_in_roi": (cx, cy),
                            "abs_pos": (cx + x_offset, cy + y_offset),
                            "dist_to_back": np.linalg.norm(np.array([cx, cy]) - np.array([FROG_RADIUS, FROG_RADIUS]))
                        })

    back_ball = None
    mouth_ball = None
    
    if found_colors:
        found_colors.sort(key=lambda x: x["dist_to_back"])
        
        back_ball = found_colors[0] # الأقرب للمركز هي الظهر
        
        if len(found_colors) > 1:
            mouth_ball = found_colors[1] # الأبعد هي الفم

    return back_ball, mouth_ball, (x_offset, y_offset, FROG_RADIUS * 2)

def get_color_mask(hsv_roi, color_name):

    if color_name == "Green":

        return cv2.inRange(hsv_roi, np.array([50, 120, 125]),np.array([75, 255, 255]))
    
    elif color_name == "Blue":
        return cv2.inRange(hsv_roi, np.array([100, 110, 120]), np.array([130, 255, 255]))
    
    elif color_name == "Yellow":
        return cv2.inRange(hsv_roi, np.array([20, 150, 120]), np.array([35, 255, 255]))
    
    elif color_name == "Purple":
        return cv2.inRange(hsv_roi, np.array([135, 110, 120]), np.array([158, 255, 255]))
    
    return np.zeros(hsv_roi.shape[:2], dtype=np.uint8)