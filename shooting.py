import pyautogui  
import time


# ==============================
# 🆕 نظام التصويب والنقر
# ==============================
class ShootingSystem:
    def __init__(self):
        self.last_shot_time = 0
        self.shot_cooldown = 0.8 
        self.last_target_id = None
        self.shots_count = 0
        
    def can_shoot(self):
    
        return time.time() - self.last_shot_time >= self.shot_cooldown
    
    def aim_and_shoot(self, target_pos, game_region, mouth_pos=None):
      
        if not self.can_shoot():
            return False
        
        # حساب الموقع المطلق على الشاشة
        screen_x = game_region["left"] + target_pos[0]
        screen_y = game_region["top"] + target_pos[1]
        
        try:
            # حرك الماوس للهدف مباشرة
            pyautogui.moveTo(screen_x, screen_y, duration=0.05)
            
            pyautogui.click()
            
            self.last_shot_time = time.time()
            self.shots_count += 1
            
            print(f"🎯 [SHOT #{self.shots_count}] at screen ({screen_x}, {screen_y})")
            return True
            
        except Exception as e:
            print(f"❌ Shot failed: {e}")
            return False