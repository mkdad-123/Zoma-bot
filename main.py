import cv2
import mss
import keyboard
import numpy as np
import pyautogui  

from config import *
from vision import detect_game_window
from Controller import GameController


pyautogui.FAILSAFE = True 
pyautogui.PAUSE = 0.01 


# ======================================================
# Entry Point
# ======================================================
def run_bot():
    print("🎯 Focus the game window and press 'S'")
    keyboard.wait('s')

    controller = GameController()

    with mss.mss() as sct:
        monitor = sct.monitors[1]

        screenshot = np.array(sct.grab(monitor))
        frame0 = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)

        bounds = detect_game_window(frame0)
        if bounds:
            x, y, w, h = bounds
            game_region = {"top": y, "left": x, "width": w, "height": h}
            print("Game window locked")
        else:
            game_region = monitor
            print("Using full screen")

        while True:
            img = np.array(sct.grab(game_region))
            frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

            controller.handle_input()
            controller.locate_frog_if_needed(frame)

            annotated, chain = controller.detect_chain(frame)
            back_ball, mouth_ball = controller.detect_frog_balls(frame, annotated)

            target, angle = controller.handle_targeting(
                annotated, chain, mouth_ball, game_region
            )

            controller.draw_hud(annotated, target, angle)
            controller.draw_auto_status(annotated)
            controller.render(annotated)

            if keyboard.is_pressed('esc') or cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cv2.destroyAllWindows()
    print(f"Total shots fired: {controller.shooter.shots_count}")


if __name__ == "__main__":
    run_bot()
