import numpy as np
import math

class TargetSelector:
    def __init__(self, frog_pos, hole_weight=1.0):
        self.frog_pos = np.array(frog_pos)
        self.hole_weight = hole_weight
    def _fallback_single_match(self, chain, mouth_color):
        best = None
        best_score = -9999

        for i, ball in enumerate(chain):
            if ball["color"] != mouth_color:
                continue

            score = 0

       
            danger_ratio = ball["chain_idx"] / len(chain)
            if danger_ratio > 0.85:
                score -= 200
            else:
                score += 30

        # زاوية منطقية
            score += self._score_angle(ball["pos"])

            if score > best_score:
                best_score = score
                best = {
                "pos": ball["pos"],
                "chain_idx": i,
                "score": score,
                "reason": "FALLBACK_SINGLE"
            }

        return best

   
    def select(self, chain, mouth_ball):
        if not chain or not mouth_ball:
            return None

        colors = [b["color"] for b in chain]
        mouth_color = mouth_ball["color"]

        best = None
        best_score = -9999

        for i in range(len(chain) + 1):

            if not self._is_logical_insert(colors, i, mouth_color):
                continue

            sim = colors[:i] + [mouth_color] + colors[i:]
            run = self._count_run(sim, i, mouth_color)

            if run < 3:
                continue

            score = 0
            score += self._score_run(run)
            score += self._score_near_hole(chain, i)
            score += self._score_split(sim, i, mouth_color)

            insert_pos = self._get_insert_point(chain, i)
            score += self._score_angle(insert_pos)

            if score > best_score:
                best_score = score
                best = {
                    "pos": insert_pos,
                    "chain_idx": i,
                    "score": score,
                    "reason": f"RUN_{run}"
                }

        if best:
            return best

        fallback = self._fallback_single_match(chain, mouth_color)
        if fallback:
            return fallback

# # ========================
# # 🟢 استراتيجة جديدة: إذا ما في أي كرة تطابق اللون
# # ========================
#         match_exists = any(ball["color"] == mouth_color for ball in chain)
#         if not match_exists and chain:
#     # اختار آخر كرة كمؤشر، وارمي لمكان فارغ أمامها
#             last_pos = chain[-1]["pos"]
#             target_pos = (last_pos[0] + 50, last_pos[1])  # تقدير 50px للأمام
#             return {
#                 "pos": target_pos,
#                 "chain_idx": len(chain),
#                 "score": 10,  # درجة منخفضة حتى لا تتغلب على القرارات الطبيعية
#                 "reason": "TEMP_MOVE"
#     }

        return None

        

    def _is_logical_insert(self, colors, i, color):
        left = colors[i - 1] if i > 0 else None
        right = colors[i] if i < len(colors) else None

        if color == left or color == right:
            return True

        if left == right and left is not None:
            return True

        return False


    def _count_run(self, sim, idx, color):
        count = 1
        i = idx - 1
        while i >= 0 and sim[i] == color:
            count += 1
            i -= 1

        i = idx + 1
        while i < len(sim) and sim[i] == color:
            count += 1
            i += 1

        return count

    def _score_run(self, run):
        if run >= 5:
            return 200
        if run == 4:
            return 150
        if run == 3:
            return 120
        return -100


    def _score_near_hole(self, chain, idx):
        if idx >= len(chain):
            return 0

        danger_ratio = chain[idx]["chain_idx"] / len(chain)

        if danger_ratio > 0.95:  # ⚡ أقرب ما يمكن للحفرة
           return int(200 * self.hole_weight)  # زيادة النقاط بشكل كبير
        elif danger_ratio > 0.85:
           return int(120 * self.hole_weight)  # درجة عالية
        elif danger_ratio > 0.6:
           return int(50 * self.hole_weight)

        return 0


    def _score_split(self, sim, idx, color):
        score = 0

        if idx > 1 and idx < len(sim) - 2:
            if sim[idx - 2] == sim[idx - 1] == sim[idx + 1]:
                score += 80

        return score

    def _get_insert_point(self, chain, i):
        if i == 0:
            return chain[0]["pos"]

        if i >= len(chain):
            return chain[-1]["pos"]

        p1 = np.array(chain[i - 1]["pos"])
        p2 = np.array(chain[i]["pos"])
        return tuple(((p1 + p2) / 2).astype(int))

    def _score_angle(self, target_pos):
        vec = np.array(target_pos) - self.frog_pos
        angle = math.degrees(math.atan2(vec[1], vec[0]))

        # زاوية مستقيمة = أفضل
        return -abs(angle) * 0.5
