import cv2
import numpy as np

# ==============================
# Load Frog Template
# ==============================
_FROG_TEMPLATE = cv2.imread("assets/frog_template.png", cv2.IMREAD_GRAYSCALE)
if _FROG_TEMPLATE is None:
    raise RuntimeError("frog_template.png not found")

# ==============================
# ORB Initialization
# ==============================
# زدنا nfeatures لضمان التقاط تفاصيل كافية حتى أثناء الدوران
_ORB = cv2.ORB.create(
    nfeatures=1200,
    scaleFactor=1.2,
    nlevels=8,
    edgeThreshold=31 # حماية من الحواف الميتة
)

_TPL_KP, _TPL_DES = _ORB.detectAndCompute(_FROG_TEMPLATE, None)
_TPL_H, _TPL_W = _FROG_TEMPLATE.shape

def locate_frog(frame, debug=False):
    """
    Detect frog position with outlier rejection (RANSAC) for high stability.
    """
    if frame is None:
        return None, None, None

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    kp_frame, des_frame = _ORB.detectAndCompute(gray, None)

    # التحقق من وجود واصفات كافية
    if des_frame is None or len(kp_frame) < 15:
        return None, None, None

    # مطابقة النقاط
    matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = matcher.match(_TPL_DES, des_frame)

    # إذا كانت المطابقات قليلة جداً، نخرج فوراً
    if len(matches) < 10:
        return None, None, None

    # ترتيب المطابقات حسب الجودة (المسافة الأقل) واختيار الأفضل
    matches = sorted(matches, key=lambda x: x.distance)[:40]

    # تحويل النقاط إلى تنسيق مصفوفة لمعالجتها هندسياً
    pts_tpl = np.float32([_TPL_KP[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
    pts_frm = np.float32([kp_frame[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)

    # --- الفلترة السحرية (RANSAC) ---
    # تبحث عن أفضل "نموذج هندسي" يجمع النقاط وتستبعد أي نقطة تشذ عنه
    _, mask = cv2.findHomography(pts_tpl, pts_frm, cv2.RANSAC, 5.0)

    if mask is None:
        return None, None, None

    # استخراج النقاط الصحيحة فقط (Inliers)
    inliers = pts_frm[mask.ravel() == 1]

    if len(inliers) < 6:
        return None, None, None

    # حساب المركز باستخدام "الوسيط" (Median) لضمان ثبات تام وعدم القفز
    all_x = [p[0][0] for p in inliers]
    all_y = [p[0][1] for p in inliers]
    
    raw_center_x = int(np.median(all_x))
    raw_center_y = int(np.median(all_y))

    OFFSET_X = 5 
    OFFSET_Y = 0
    
    
    center_x = raw_center_x + OFFSET_X
    center_y = raw_center_y + OFFSET_Y
    center = (center_x, center_y)

    # في زوما، حجم الضفدع ثابت لا يتغير، لذا نستخدم حجم تقريبي ثابت
    # هذا يمنع اهتزاز الدائرة (Radius) ويجعلها ثابتة على جسم الضفدع
    radius = 115
    
    # حساب الـ Bounding Box بناءً على المركز ليكون مستقراً أيضاً
    x = int(center_x - radius)
    y = int(center_y - radius)
    w = h = int(radius * 2)
    x = max(0, x)
    y = max(0, y)
    
    bbox = (x, y, w, h)

    if debug:
        dbg = frame.copy()
        # رسم نقاط المطابقة الصحيحة فقط باللون الأخضر
        for p in inliers:
            cv2.circle(dbg, (int(p[0][0]), int(p[0][1])), 3, (0, 255, 0), -1)
        
        # رسم المركز والحدود
        cv2.circle(dbg, center, 5, (0, 0, 255), -1)
        cv2.circle(dbg, center, radius, (255, 255, 0), 2)
        cv2.imshow("Frog Stable Detection", dbg)

    return center, radius, bbox