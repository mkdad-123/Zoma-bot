import cv2
import mss
import keyboard
import time
import numpy as np
from config import *
from vision import detect_game_window, detect_balls , detect_frog_balls
from utils import show_fps, resize_widow , set_window

current_ball = None
next_ball = None

# ==============================
# Main Loop
# ==============================


def run_bot():
    print("Focus the game window and press 'S' to lock it...")
    keyboard.wait('s')

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
        img = np.array(sct.grab(game_region))
        frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        cv2.imwrite("frog_calibration.png", frame)

        window_name = set_window()

        last_time = time.time()

        while True:

            img = np.array(sct.grab(game_region))
            frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

            if frame.shape[1] != game_region["width"] or frame.shape[0] != game_region["height"]:
                print("Game size changed. Re-locking ROI...")
                bounds = detect_game_window(frame)

            annotated, balls = detect_balls(frame)
            
            current_ball, next_ball, mouth_pos, back_pos = detect_frog_balls(
                frame,
                back_ball_center=FROG_CENTER,
                frog_radius=FROG_RADIUS
            )

            if back_pos:
                cv2.circle(frame, back_pos, 8, (255, 255, 255), 2)
                cv2.putText(frame, f"Next: {next_ball}", (back_pos[0]+10, back_pos[1]),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 2)

            if mouth_pos:
                cv2.circle(frame, mouth_pos, 8, (0, 255, 0), 2)
                cv2.putText(frame, f"Current: {current_ball}", (mouth_pos[0]+10, mouth_pos[1]),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)


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
