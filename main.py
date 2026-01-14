import cv2
import mss
import keyboard
import time
import numpy as np
import pyautogui  

from config import *
from utils import show_fps, resize_widow, set_window, compute_angle
from vision import detect_game_window, detect_balls
from vision_frog import get_frog_balls_by_color
from graph_chain import build_ball_graph, find_chain
from strategy import TargetSelector
from ball_tracker import BallTracker
from vision_frog_locator import locate_frog
from shooting import ShootingSystem



pyautogui.FAILSAFE = True 
pyautogui.PAUSE = 0.01 


# ==============================
# Main Loop
# ==============================
def run_bot():
    print("🎯 Focus the game window and press 'S' to lock it...")
    keyboard.wait('s')

    # تهيئة الأنظمة
    tracker = BallTracker()
    shooter = ShootingSystem()  # 🆕 نظام التصويب

    # 🆕 وضع التشغيل
    auto_mode = True  # ✅ التحكم التلقائي مفعل من البداية
    print("⌨️  Press 'A' to toggle AUTO mode (Currently: ON)")
    print("⌨️  Press 'ESC' to quit")
    print("🎮 Bot will shoot automatically!")

    with mss.mss() as sct:
        monitor = sct.monitors[1]

        # ==========================
        # Detect Game Window (once)
        # ==========================
        screenshot = np.array(sct.grab(monitor))
        initial_frame = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)

        bounds = detect_game_window(initial_frame)

        if bounds:
            x, y, w, h = bounds
            print(f"✅ Game window locked: {w}x{h}")
            game_region = {"top": y, "left": x, "width": w, "height": h}
        else:
            print("⚠️ Game window not detected, using full screen.")
            game_region = monitor

        frog_center = None
        frog_radius = None
        
        window_name = set_window()
        last_time = time.time()

        print("▶ Bot started - Sequential tracking + Mouse control enabled")

        # ==========================
        # Main Frame Loop
        # ==========================
        while True:
            # 🆕 تبديل الوضع التلقائي
            if keyboard.is_pressed('a'):
                auto_mode = not auto_mode
                status = "ON ✅" if auto_mode else "OFF ❌"
                print(f"🤖 AUTO MODE: {status}")
                time.sleep(0.3)  # تجنب التكرار

            img = np.array(sct.grab(game_region))
            frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

            # ==========================
            # 1️⃣ Locate Frog
            # ==========================

            # 1. التحقق من إعادة الحساب يدوياً (عند ضغط R)
            if keyboard.is_pressed('r'):
                print("Re-scanning for frog position...")
                frog_center = None 

            # 2. كشف موقع الضفدع (فقط إذا لم يكن موجوداً في الذاكرة)
            if frog_center is None:

                temp_center, temp_radius, _ = locate_frog(frame, debug=True)
                if temp_center is not None:
                    frog_center, frog_radius = temp_center, temp_radius
                    print(f"Frog locked at: {frog_center}")

            # ==========================
            # 1️⃣ Detect Balls
            # ==========================
            annotated, balls = detect_balls(frame)

            chain = []
            if len(balls) > 3:
                graph = build_ball_graph(balls)
                frog_center = BACK_BALL_CENTER

                chain = find_chain(graph, balls, frog_center)
                
                # Compute chain progress
                if len(chain) >= 2:
                    chain[0]["progress"] = 0.0
                    for i in range(1, len(chain)):
                        p_prev = np.array(chain[i - 1]["pos"])
                        p_curr = np.array(chain[i]["pos"])
                        dist = np.linalg.norm(p_curr - p_prev)
                        chain[i]["progress"] = chain[i - 1]["progress"] + dist

                chain = tracker.update(chain)

                # رسم المسار والكرات
                BallTracker.draw_enhanced_path(frame, chain)
                BallTracker.draw_ball_numbers(frame, chain)
                BallTracker.draw_ball_indicators(frame, chain)

            # ==========================
            # 2️⃣ Detect Frog Balls
            # ==========================

            if frog_center:
                back_ball, mouth_ball, roi_box = get_frog_balls_by_color(frame ,frog_center, frog_radius )

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

            # ==========================
            # 3️⃣ Target Selection
            # ==========================
            target = None
            if mouth_ball is not None and chain:
                selector = TargetSelector(BACK_BALL_CENTER)
                target = selector.select(chain, mouth_ball)

            # تنفيذ الإطلاق فقط إذا وجدنا هدفاً وكانت الكرة موجودة
            if target and mouth_ball:
                tx, ty = target["pos"]
                
                # رسم الهدف - دوائر متحركة
                cv2.circle(annotated, (tx, ty), 25, (0, 255, 0), 3)
                cv2.circle(annotated, (tx, ty), 15, (0, 255, 0), 2)
                cv2.circle(annotated, (tx, ty), 5, (0, 255, 0), -1)
                
                # علامة X على الهدف
                offset = 8
                cv2.line(annotated, (tx-offset, ty-offset), (tx+offset, ty+offset), (0, 255, 0), 2)
                cv2.line(annotated, (tx+offset, ty-offset), (tx-offset, ty+offset), (0, 255, 0), 2)

                # ==========================
                # 4️⃣ خط التصويب
                # ==========================
                angle = compute_angle(
                    mouth_ball["abs_pos"],
                    target["pos"]
                )

                mx, my = mouth_ball["abs_pos"]
                
                # خط رفيع رمادي
                cv2.line(annotated, (mx, my), (tx, ty), (100, 100, 100), 1)
                
                # سهم سميك
                cv2.arrowedLine(
                    annotated,
                    (mx, my),
                    (tx, ty),
                    (255, 0, 255),
                    3,
                    tipLength=0.15
                )

                # ==========================
                # 🆕 5️⃣ التصويب التلقائي
                # ==========================
                if auto_mode:
                    shot_success = shooter.aim_and_shoot(
                        (tx, ty),
                        game_region
                    )
                    
                    if shot_success:
                        # رسم مؤثر بصري للطلقة
                        cv2.circle(annotated, (tx, ty), 40, (0, 255, 0), 3)
                        print(f"✅ Shot fired at target #{target['chain_idx']}")

                # عرض المعلومات

                info_box_y = 100
                cv2.rectangle(annotated, (5, info_box_y), (200, info_box_y + 100), (0, 0, 0), -1)
                cv2.rectangle(annotated, (5, info_box_y), (200, info_box_y + 100), (255, 255, 255), 2)
                
                cv2.putText(
                    annotated,
                    f"Target: #{target['chain_idx']}",
                    (15, info_box_y + 25),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 255, 255),
                    1
                )
                
                cv2.putText(
                    annotated,
                    f"Angle: {angle:.1f}",
                    (15, info_box_y + 45),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (255, 0, 255),
                    1
                )
                
                cv2.putText(
                    annotated,
                    f"Score: {target['score']}",
                    (15, info_box_y + 65),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 255, 0),
                    1
                )
                
                # 🆕 عرض عدد الطلقات
                cv2.putText(
                    annotated,
                    f"Shots: {shooter.shots_count}",
                    (15, info_box_y + 85),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (255, 255, 0),
                    1
                )

            else:
                if len(balls) > 0:
                    cv2.putText(
                        annotated,
                        "Waiting for target...",
                        (10, 110),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        (0, 165, 255),
                        2
                    )

            # ==========================
            # 🆕 عرض حالة الوضع التلقائي
            # ==========================
            mode_text = "AUTO: ON" if auto_mode else "AUTO: OFF"
            mode_color = (0, 255, 0) if auto_mode else (0, 0, 255)
            
            cv2.rectangle(annotated, (5, 5), (150, 45), (0, 0, 0), -1)
            cv2.rectangle(annotated, (5, 5), (150, 45), mode_color, 2)
            cv2.putText(
                annotated,
                mode_text,
                (15, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                mode_color,
                2
            )

            # عرض عدد الكرات

            cv2.putText(
                annotated,
                f"Balls: {len(chain)}",
                (170, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2
            )

            # FPS + Preview

            last_time = show_fps(last_time, annotated)

            preview = resize_widow(
                annotated,
                PREVIEW_SCALE_PERCENT / 100
            )
            cv2.imshow(window_name, preview)

            if keyboard.is_pressed('esc') or cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cv2.destroyAllWindows()
    print(f"\n📊 Total shots fired: {shooter.shots_count}")


# ==============================
# Entry Point
# ==============================
if __name__ == "__main__":
    run_bot()