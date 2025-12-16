# import library ที่ใช้
import cv2
import mediapipe as mp
import math

# เปิดกล้องเว็บแคม (Windows แนะนำ)
webcam = cv2.VideoCapture(0, cv2.CAP_DSHOW)

# เตรียม MediaPipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)
mp_draw = mp.solutions.drawing_utils

while True:
    success, image = webcam.read()
    if not success:
        print("Ignoring empty camera frame.")
        continue

    # กลับภาพเหมือนกระจก
    image = cv2.flip(image, 1)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hands.process(image_rgb)

    finger_count = 0

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(
                image,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS
            )

            lm = hand_landmarks.landmark
            fingers = []

            # ================== นิ้วโป้ง ==================
            thumb_tip = lm[4]
            thumb_ip  = lm[3]
            index_mcp = lm[5]

            dist_tip = math.hypot(
                thumb_tip.x - index_mcp.x,
                thumb_tip.y - index_mcp.y
            )
            dist_ip = math.hypot(
                thumb_ip.x - index_mcp.x,
                thumb_ip.y - index_mcp.y
            )

            thumb_extended = dist_tip > dist_ip + 0.02
            fingers.append(1 if thumb_extended else 0)

            # ================== นิ้วชี้–ก้อย ==================
            finger_ids = [
                (8, 6, 5),    # ชี้
                (12, 10, 9),  # กลาง
                (16, 14, 13), # นาง
                (20, 18, 17)  # ก้อย
            ]

            for tip, pip, mcp in finger_ids:
                is_extended = (
                    lm[tip].y < lm[pip].y and
                    lm[pip].y < lm[mcp].y
                )
                fingers.append(1 if is_extended else 0)

            finger_count = sum(fingers)

            # แสดงผลลัพธ์บนจอ
            cv2.putText(
                image,
                f"Extended Fingers: {finger_count}",
                (20, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2
            )

    cv2.imshow("Image", image)

    if cv2.waitKey(1) == 27:  # ESC
        break

webcam.release()
cv2.destroyAllWindows()