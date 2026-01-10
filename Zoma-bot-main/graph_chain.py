import numpy as np
from collections import defaultdict
from config import UI_MASK_TOP


# ==========================
# Estimate ball spacing
# ==========================
def estimate_ball_spacing(balls):
    dists = []
    for i in range(len(balls)):
        for j in range(i + 1, len(balls)):
            p1 = np.array(balls[i]["pos"])
            p2 = np.array(balls[j]["pos"])
            d = np.linalg.norm(p1 - p2)
            if 20 < d < 70:
                dists.append(d)

    return np.median(dists) if dists else 40


# ==========================
# Build Graph
# ==========================
def build_ball_graph(balls):
    spacing = estimate_ball_spacing(balls)
    max_dist = spacing * 1.35

    graph = defaultdict(list)

    for i, b1 in enumerate(balls):
        for j, b2 in enumerate(balls):
            if i == j:
                continue

            p1 = np.array(b1["pos"])
            p2 = np.array(b2["pos"])
            dist = np.linalg.norm(p1 - p2)

            if dist <= max_dist:
                graph[i].append(j)

    return graph


# ==========================
# Helpers
# ==========================
def is_inside_top_ui(ball):
    """نحدد إن كانت الكرة داخل شريط الـ UI"""
    return ball["pos"][1] < UI_MASK_TOP["height"]


def get_degree(graph, idx):
    return len(graph.get(idx, []))


# ==========================
# Find Chain (FINAL LOGIC)
# ==========================
def find_chain(graph, balls, frog_center):
    if not graph:
        return []

    # --------------------------
    # 1️⃣ تحديد الـ endpoints (مع استثناء UI)
    # --------------------------
    endpoints = [
        i for i in graph
        if get_degree(graph, i) == 1 and not is_inside_top_ui(balls[i])
    ]

    # fallback إذا ما لقينا endpoints
    if not endpoints:
        endpoints = [
            i for i in graph
            if not is_inside_top_ui(balls[i])
        ]

    if not endpoints:
        return []

    # --------------------------
    # 2️⃣ اختيار البداية الأقرب للضفدع
    # --------------------------
    frog = np.array(frog_center)

    start = min(
        endpoints,
        key=lambda i: np.linalg.norm(np.array(balls[i]["pos"]) - frog)
    )

    # --------------------------
    # 3️⃣ Walk graph (بدون قطع عند UI)
    # --------------------------
    chain = []
    visited = set()
    current = start
    prev = None

    while current is not None:
        chain.append(balls[current])
        visited.add(current)

        neighbors = graph[current]

        next_nodes = [
            n for n in neighbors
            if n != prev and n not in visited
        ]

        if not next_nodes:
            break

        # اختر الجار الأقرب هندسيًا
        curr_pos = np.array(balls[current]["pos"])
        next_node = min(
            next_nodes,
            key=lambda n: np.linalg.norm(
                np.array(balls[n]["pos"]) - curr_pos
            )
        )

        prev = current
        current = next_node

    return chain
