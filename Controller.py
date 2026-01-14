import cv2
import keyboard
import time
import numpy as np

from config import *
from utils import show_fps, resize_widow, set_window, compute_angle
from vision import detect_balls
from vision_frog import get_frog_balls_by_color
from vision_frog_locator import locate_frog
from graph_chain import build_ball_graph, find_chain
from strategy import TargetSelector
from ball_tracker import BallTracker
from shooting import ShootingSystem


# ======================================================
# Game Controller
# ======================================================
class GameController:

    def __init__(self):
        self.tracker = BallTracker()
        self.shooter = ShootingSystem()
        self.selector = TargetSelector(BACK_BALL_CENTER)

        self.auto_mode = True
        self.frog_center = None
        self.frog_radius = None

        self.last_time = time.time()
        self.window_name = set_window()

        print("⌨️  Press 'A' to toggle AUTO mode")
        print("⌨️  Press 'R' to re-scan frog")
        print("⌨️  Press 'ESC' to quit")


    # --------------------------------------------------
    # Input Handling
    # --------------------------------------------------
    def handle_input(self):
        if keyboard.is_pressed('a'):
            self.auto_mode = not self.auto_mode
            status = "ON ✅" if self.auto_mode else "OFF ❌"
            print(f"AUTO MODE: {status}")
            time.sleep(0.3)

        if keyboard.is_pressed('r'):
            print("Re-scanning frog position...")
            self.frog_center = None



    # --------------------------------------------------
    # Frog Detection
    # --------------------------------------------------
    def locate_frog_if_needed(self, frame):
        if self.frog_center is None:
            center, radius, _ = locate_frog(frame, debug=True)
            if center is not None:
                self.frog_center = center
                self.frog_radius = radius
                print(f"Frog locked at {center}")


    # --------------------------------------------------
    # Ball Detection & Chain Tracking
    # --------------------------------------------------
    def detect_chain(self, frame):
        annotated, balls = detect_balls(frame)
        chain = []

        if len(balls) > 3:
            graph = build_ball_graph(balls)

            chain = find_chain(graph, balls, BACK_BALL_CENTER)

            if len(chain) >= 2:
                chain[0]["progress"] = 0.0
                for i in range(1, len(chain)):
                    p1 = np.array(chain[i - 1]["pos"])
                    p2 = np.array(chain[i]["pos"])
                    chain[i]["progress"] = chain[i - 1]["progress"] + np.linalg.norm(p2 - p1)

            chain = self.tracker.update(chain)

            BallTracker.draw_enhanced_path(annotated, chain)
            BallTracker.draw_ball_numbers(annotated, chain)
            BallTracker.draw_ball_indicators(annotated, chain)

            
        return annotated, chain


    # --------------------------------------------------
    # Frog Balls Detection
    # --------------------------------------------------
    def detect_frog_balls(self, frame, annotated):
        if not self.frog_center:
            return None, None

        back_ball, mouth_ball, roi_box = get_frog_balls_by_color(
            frame,
            self.frog_center,
            self.frog_radius
        )

        rx, ry, rsize = roi_box
        cv2.rectangle(annotated, (rx, ry), (rx + rsize, ry + rsize), (255, 255, 255), 2)

        if back_ball:
            color = back_ball["color"]
            cv2.putText(annotated, f"Back: {color}", (rx, ry - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, COLOR_DRAW_MAP[color], 2)
            cv2.circle(annotated, back_ball["abs_pos"], 5, (255, 255, 255), -1)

        if mouth_ball:
            color = mouth_ball["color"]
            cv2.putText(annotated, f"Mouth: {color}", (rx, ry + rsize + 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, COLOR_DRAW_MAP[color], 2)
            cv2.circle(annotated, mouth_ball["abs_pos"], 8, (0, 255, 255), 2)

        return back_ball, mouth_ball


    # --------------------------------------------------
    # Target Selection & Shooting
    # --------------------------------------------------
    def handle_targeting(self, annotated, chain, mouth_ball, game_region):
        if not chain or not mouth_ball:
            return None, None

        target = self.selector.select(chain, mouth_ball)
        if not target:
            return None, None

        tx, ty = target["pos"]
        mx, my = mouth_ball["abs_pos"]

        angle = compute_angle((mx, my), (tx, ty))

        cv2.arrowedLine(annotated, (mx, my), (tx, ty),
                        (255, 0, 255), 3)

        if self.auto_mode:
            if self.shooter.aim_and_shoot((tx, ty), game_region):
                print(f"Shot fired at target #{target['chain_idx']}")

        return target, angle



    # --------------------------------------------------
    # Rendering
    # --------------------------------------------------
    def render(self, annotated):
        self.last_time = show_fps(self.last_time, annotated)

        preview = resize_widow(
            annotated,
            PREVIEW_SCALE_PERCENT / 100
        )

        cv2.imshow(self.window_name, preview)


    def draw_hud(self, annotated, target, angle):
        info_box_y = 100
        cv2.rectangle(annotated, (5, info_box_y), (200, info_box_y + 100), (0, 0, 0), -1)
        cv2.rectangle(annotated, (5, info_box_y), (200, info_box_y + 100), (255, 255, 255), 2)

        if target:
            cv2.putText(annotated, f"Target: #{target['chain_idx']}",
                        (15, info_box_y + 25),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

            cv2.putText(annotated, f"Angle: {angle:.1f}",
                        (15, info_box_y + 45),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 1)

            cv2.putText(annotated, f"Score: {target['score']:.3f}",
                        (15, info_box_y + 65),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        cv2.putText(annotated, f"Shots: {self.shooter.shots_count}",
                    (15, info_box_y + 85),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)


    def draw_auto_status(self, annotated):
        mode_text = "AUTO: ON" if self.auto_mode else "AUTO: OFF"
        mode_color = (0, 255, 0) if self.auto_mode else (0, 0, 255)

        cv2.rectangle(annotated, (5, 5), (150, 45), (0, 0, 0), -1)
        cv2.rectangle(annotated, (5, 5), (150, 45), mode_color, 2)
        cv2.putText(annotated, mode_text,
                    (15, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, mode_color, 2)
