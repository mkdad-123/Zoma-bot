import cv2
import mss
import keyboard
import time
import numpy as np
from config import *
from vision import detect_game_window, detect_balls  , detect_next_ball
from utils import show_fps, resize_widow , set_window
from vision_frog import get_frog_balls_by_color



# ==============================
# Main Loop
# ==============================


def run_bot():
    print("Focus the game window and press 'S' to lock it...")
    keyboard.wait('s')
    
    current_ball = None
    next_ball = None
    initialized = False
    last_shot_time = 0

    with mss.mss() as sct:
        monitor = sct.monitors[1]
        screenshot = np.array(sct.grab(monitor))
        initial_frame = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)

        cv2.imwrite("frog_calibration.png", initial_frame)

        bounds = detect_game_window(initial_frame)

        if bounds:
            x, y, w, h = bounds
            print(f"Target locked: {w}x{h}")
            game_region = {"top": y, "left": x, "width": w, "height": h}
        else:
            print("Game window not detected, using full screen.")
            game_region = monitor
    

        window_name = set_window()

        last_time = time.time()

        while True:

            img = np.array(sct.grab(game_region))
            frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

            if frame.shape[1] != game_region["width"] or frame.shape[0] != game_region["height"]:
                print("Game size changed. Re-locking ROI...")
                bounds = detect_game_window(frame)

            scale = PREVIEW_SCALE_PERCENT / 100




            annotated, balls = detect_balls(frame)

            # هون بكشف كرات الضفدع 
            back_ball, mouth_ball, roi_box = get_frog_balls_by_color(frame)

            # الرسم لاعرف شاغل صح 
            rx, ry, rsize = roi_box
            # عم ارسم مربع الـ ROI حول الضفدع
            cv2.rectangle(annotated, (rx, ry), (rx + rsize, ry + rsize), (255, 255, 255), 2)
            
            if back_ball:
                color = back_ball['color']
                cv2.putText(annotated, f"Back: {color}", (rx, ry - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, COLOR_DRAW_MAP[color], 2)
                cv2.circle(annotated, back_ball['abs_pos'], 5, (255, 255, 255), -1)

            if mouth_ball:
                color = mouth_ball['color']
                cv2.putText(annotated, f"Mouth: {color}", (rx, ry + rsize + 20), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, COLOR_DRAW_MAP[color], 2)
                cv2.circle(annotated, mouth_ball['abs_pos'], 8, (0, 255, 255), 2)



                # حسبت FPS
            last_time = show_fps(last_time, annotated)

        
            # Preview scaling (visual only) ما بتتغير الجودة عند التحليل
            scale = PREVIEW_SCALE_PERCENT / 100
            resized = resize_widow(annotated, scale)

            cv2.imshow(window_name, resized)

            if keyboard.is_pressed('esc') or cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cv2.destroyAllWindows()


# ==============================
# Entry Point
# ==============================

if __name__ == "__main__":
    run_bot()
