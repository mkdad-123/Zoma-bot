import cv2
import mss
import keyboard
import time
import numpy as np
from config import *
from vision import detect_game_window, detect_balls
from utils import show_fps, resize_widow , set_window
from vision_frog import get_frog_balls_by_color
from vision_frog_locator import locate_frog


# ==============================
# Main
# ==============================

def run_bot():
    print("Focus the game window and press 'S' to lock it...")
    keyboard.wait('s')
    
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        screenshot = np.array(sct.grab(monitor))
        initial_frame = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)

        bounds = detect_game_window(initial_frame)

        if bounds:
            x, y, w, h = bounds
            print(f"Target locked: {w}x{h}")
            game_region = {"top": y, "left": x, "width": w, "height": h}
        else:
            print("Game window not detected, using full screen.")
            game_region = monitor
    
        # متغيرات تخزين موقع الضفدع
        frog_center = None
        frog_radius = None
        window_name = set_window()

        last_time = time.time()

        print("Controls: 'ESC' to Quit, 'R' to Re-locate Frog")

        while True:
            img = np.array(sct.grab(game_region))
            frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

            # 1. التحقق من إعادة الحساب يدوياً (عند ضغط R)
            if keyboard.is_pressed('r'):
                print("Re-scanning for frog position...")
                frog_center = None # تصفير الموقع لإجباره على البحث مرة أخرى

            # 2. كشف موقع الضفدع (فقط إذا لم يكن موجوداً في الذاكرة)
            if frog_center is None:
                # هذه العملية ثقيلة (ORB)، لذا ستعمل مرة واحدة فقط
                temp_center, temp_radius, _ = locate_frog(frame, debug=True)
                if temp_center is not None:
                    frog_center, frog_radius = temp_center, temp_radius
                    print(f"Frog locked at: {frog_center}")

            # 3. تحليل الكرات (تعمل في كل فريم)
            annotated, balls = detect_balls(frame)

            # 4. إذا كان الضفدع موجوداً، ابحث عن كراته
            if frog_center:
                # كشف كرات الضفدع (عملية خفيفة تعتمد على اللون داخل ROI ثابت)
                back_ball, mouth_ball, roi_box = get_frog_balls_by_color(
                    frame,
                    frog_center,
                    frog_radius
                )

                # الرسم للتأكد
                rx, ry, rsize = roi_box
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

            # حساب FPS وعرض الصورة
            last_time = show_fps(last_time, annotated)
            scale = PREVIEW_SCALE_PERCENT / 100
            resized = resize_widow(annotated, scale)
            cv2.imshow(window_name, resized)

            # الخروج
            if keyboard.is_pressed('esc') or cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    run_bot()