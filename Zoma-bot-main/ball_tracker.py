import numpy as np
import cv2
from config import *
# ==============================
# تتبع الكرات بين الإطارات
# ==============================
class BallTracker:
    def __init__(self):
        self.tracked_balls = []
        self.next_id = 0
        
    def update(self, new_chain):
        """
        تحديث الكرات المتتبعة وإضافة الجديدة
        """
        if not new_chain:
            return []
        
        # إذا أول مرة، أضف كل الكرات
        if not self.tracked_balls:
            for idx, ball in enumerate(new_chain):
                ball["id"] = idx
                ball["chain_idx"] = idx
            self.tracked_balls = new_chain
            self.next_id = len(new_chain)
            return self.tracked_balls
        
        # مطابقة الكرات القديمة مع الجديدة
        matched = []
        unmatched_new = []
        
        for new_ball in new_chain:
            # ابحث عن أقرب كرة قديمة بنفس اللون
            best_match = None
            best_dist = float('inf')
            
            for old_ball in self.tracked_balls:
                if old_ball["color"] == new_ball["color"]:
                    dist = np.linalg.norm(
                        np.array(new_ball["pos"]) - np.array(old_ball["pos"])
                    )
                    
                    if dist < 30 and dist < best_dist:  # عتبة المسافة
                        best_dist = dist
                        best_match = old_ball
            
            if best_match:
                # كرة موجودة - احتفظ بالـ ID
                new_ball["id"] = best_match["id"]
                matched.append(new_ball)
            else:
                # كرة جديدة
                unmatched_new.append(new_ball)
        
        # أضف الكرات الجديدة
        for new_ball in unmatched_new:
            new_ball["id"] = self.next_id
            self.next_id += 1
            matched.append(new_ball)
        
        # رتب حسب الموقع على المسار
        matched.sort(key=lambda b: b.get("progress", 0))
        
        # أعد ترقيم chain_idx بالتسلسل
        for idx, ball in enumerate(matched):
            ball["chain_idx"] = idx
        
        self.tracked_balls = matched
        return self.tracked_balls
    
    def draw_enhanced_path(frame, chain):
    
        if len(chain) < 2:
            return
    
    # رسم خط المسار
        points = [ball["pos"] for ball in chain]
    
        for i in range(len(points) - 1):
            p1 = points[i]
            p2 = points[i + 1]
        
        # تدرج لوني من الأخضر للأحمر (حسب القرب من النهاية)
            ratio = i / max(len(points) - 1, 1)
        
        # Green (0, 255, 0) -> Yellow (0, 255, 255) -> Red (0, 0, 255)
            if ratio < 0.5:
            # Green to Yellow
                r_ratio = ratio * 2
                color = (0, 255, int(255 * r_ratio))
            else:
            # Yellow to Red
                r_ratio = (ratio - 0.5) * 2
                color = (0, int(255 * (1 - r_ratio)), 255)
        
        # رسم خط سميك
            cv2.line(frame, p1, p2, color, 5, cv2.LINE_AA)


    def draw_ball_numbers(frame, chain):
   
        for ball in chain:
            x, y = ball["pos"]
            idx = ball["chain_idx"]
        
        # دائرة خلفية سوداء
            cv2.circle(frame, (x, y - 15), 12, (0, 0, 0), -1)
            cv2.circle(frame, (x, y - 15), 12, (255, 255, 255), 2)
        
        # النص
            text = str(idx)
            text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
            text_x = x - text_size[0] // 2
            text_y = y - 10
        
            cv2.putText(
                frame,
                text,
                (text_x, text_y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                2,
                cv2.LINE_AA
        )


    def draw_ball_indicators(frame, chain):
   
        for ball in chain:
            x, y = ball["pos"]
        
        # دائرة خارجية رفيعة بلون الكرة
            color = COLOR_DRAW_MAP.get(ball["color"], (200, 200, 200))
            cv2.circle(frame, (x, y), 18, color, 2)
        
        # نقطة في المركز
            cv2.circle(frame, (x, y), 3, (255, 255, 255), -1)


        


