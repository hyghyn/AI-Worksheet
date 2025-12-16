# ===============================
# 1) IMPORT LIBRARIES
# ===============================

import cv2                     # ใช้เปิดกล้อง, แสดงภาพ, วาดกรอบ
import numpy as np              # จัดการข้อมูลภาพแบบ array
import mediapipe as mp          # ไลบรารี AI Vision ของ Google
from mediapipe.tasks import python
from mediapipe.tasks.python import vision


# ===============================
# 2) CONFIG ค่าพื้นฐานสำหรับการแสดงผล
# ===============================

MARGIN = 10                     # ระยะห่างข้อความจากกรอบ (pixel)
ROW_SIZE = 20                   # ระยะบรรทัดข้อความ
FONT_SIZE = 1                   # ขนาดตัวอักษร
FONT_THICKNESS = 2              # ความหนาของตัวอักษร
TEXT_COLOR = (0, 255, 0)        # สีตัวอักษร (เขียว - BGR)


# ===============================
# 3) ฟังก์ชันวาดกรอบ + ชื่อวัตถุ
# ===============================

def visualize(image, detection_result):
    """
    รับภาพและผลลัพธ์จาก AI
    แล้ววาดกรอบ Bounding Box + ชื่อวัตถุ + คะแนน
    """

    # วนลูปวัตถุทุกชิ้นที่ตรวจพบ
    for detection in detection_result.detections:

        # -------------------------
        # ดึงข้อมูลกรอบ Bounding Box
        # -------------------------
        bbox = detection.bounding_box

        # มุมซ้ายบนของกรอบ
        start_point = (bbox.origin_x, bbox.origin_y)

        # มุมขวาล่างของกรอบ
        end_point = (
            bbox.origin_x + bbox.width,
            bbox.origin_y + bbox.height
        )

        # วาดกรอบสี่เหลี่ยมรอบวัตถุ
        cv2.rectangle(
            image,
            start_point,
            end_point,
            TEXT_COLOR,
            2
        )

        # -------------------------
        # ดึงชื่อวัตถุ + ความมั่นใจ
        # -------------------------
        category = detection.categories[0]      # หมวดหมู่แรก
        category_name = category.category_name  # ชื่อวัตถุ
        probability = round(category.score, 2) # คะแนนความมั่นใจ

        # ข้อความที่จะแสดง
        text = f"{category_name} ({probability})"

        # ตำแหน่งข้อความ
        text_location = (
            bbox.origin_x + MARGIN,
            bbox.origin_y + ROW_SIZE
        )

        # วาดข้อความบนภาพ
        cv2.putText(
            image,
            text,
            text_location,
            cv2.FONT_HERSHEY_SIMPLEX,
            FONT_SIZE,
            TEXT_COLOR,
            FONT_THICKNESS
        )

    # ส่งภาพที่วาดแล้วกลับไป
    return image


# ===============================
# 4) โหลดโมเดล Object Detection
# ===============================

# ระบุไฟล์โมเดล AI (.tflite)
base_options = python.BaseOptions(
    model_asset_path="efficientdet_lite0.tflite"
)

# ตั้งค่าการตรวจจับ
options = vision.ObjectDetectorOptions(
    base_options=base_options,
    score_threshold=0.5        # แสดงเฉพาะวัตถุที่มั่นใจ ≥ 50%
)

# สร้างตัวตรวจจับวัตถุ
detector = vision.ObjectDetector.create_from_options(options)


# ===============================
# 5) เปิดกล้องเว็บแคม
# ===============================

cap = cv2.VideoCapture(0)      # 0 = กล้องตัวแรก

# ตรวจสอบว่ากล้องเปิดได้หรือไม่
if not cap.isOpened():
    print("❌ ไม่สามารถเปิดกล้องได้")
    exit()


# ===============================
# 6) LOOP อ่านภาพจากกล้อง
# ===============================

while True:

    # อ่านภาพจากกล้อง
    success, frame = cap.read()

    # ถ้าอ่านภาพไม่ได้ ให้ข้ามรอบนี้
    if not success:
        print("⚠️ Ignoring empty camera frame")
        continue

    # -------------------------
    # แปลงสี BGR → RGB
    # -------------------------
    # OpenCV ใช้ BGR
    # MediaPipe ใช้ RGB
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # แปลงเป็นรูปแบบที่ MediaPipe ต้องการ
    mp_image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=frame_rgb
    )

    # -------------------------
    # ตรวจจับวัตถุด้วย AI
    # -------------------------
    detection_result = detector.detect(mp_image)

    # -------------------------
    # วาดกรอบและข้อความ
    # -------------------------
    annotated_image = visualize(
        frame.copy(),
        detection_result
    )

    # -------------------------
    # แสดงผลบนหน้าจอ
    # -------------------------
    cv2.imshow("Object Detection", annotated_image)

    # กด ESC (27) เพื่อออกจากโปรแกรม
    if cv2.waitKey(1) & 0xFF == 27:
        break


# ===============================
# 7) ปิดกล้องและหน้าต่าง
# ===============================

cap.release()                  # ปิดกล้อง
cv2.destroyAllWindows()        # ปิดทุกหน้าต่าง
