# import library ที่ใช้
import cv2
import mediapipe as mp

# เปิดกล้องเว็บแคม
webcam = cv2.VideoCapture(0)
success, image = webcam.read()   # แก้ให้รับค่าให้ถูกต้อง

# เตรียมโมดูลสำหรับตรวจจับมือ
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_draw = mp.solutions.drawing_utils

# วนลูปอ่านค่าจากกล้องและหาตำแหน่งของมือ
while True:
    success, image = webcam.read()
    if not success:
        print("Ignoring empty camera frame.")
        continue

    image = cv2.flip(image, 1)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hands.process(image_rgb)
    imageHeight, imageWidth, _ = image.shape

    count = 0   # ย้ายออกมานอก if เพื่อไม่ให้ error

    if results.multi_hand_landmarks:
        for landmark in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(image, landmark, mp_hands.HAND_CONNECTIONS)

        for hand_landmarks in results.multi_hand_landmarks:
            print('Handedness:', results.multi_handedness)

            for point in mp_hands.HandLandmark:
                normalizedLandmark = hand_landmarks.landmark[point]
                pixelCoordinatesLandmark = mp_draw._normalized_to_pixel_coordinates(
                    normalizedLandmark.x,
                    normalizedLandmark.y,
                    imageWidth,
                    imageHeight
                )

                print(point)
                print(pixelCoordinatesLandmark)
                # print(normalizedLandmark)

            count += 1   # นับจำนวนมือ

    print("Number of hands = ", count)

    # แสดงผลลัพธ์ออกทางหน้าจอ
    cv2.imshow("Image", cv2.flip(image, 1))
    k = cv2.waitKey(1)
    if k == 27:   # กด ESC เพื่อออก
        break

cv2.destroyAllWindows()