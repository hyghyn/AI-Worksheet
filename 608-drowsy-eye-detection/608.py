import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# ฟังก์ชันคำนวณระยะแนวตั้งระหว่างจุด min-max ของแกน y
def open_len(arr):
    y_arr = []
    
    for _, y in arr:
        y_arr.append(y)
    
    min_y = min(y_arr)
    max_y = max(y_arr)
    
    return max_y - min_y

# โหลด face_landmarker.task model
model_path = 'face_landmarker.task'

# สร้าง FaceLandmarker options
base_options = python.BaseOptions(model_asset_path=model_path)
options = vision.FaceLandmarkerOptions(
    base_options=base_options,
    output_face_blendshapes=False,
    output_facial_transformation_matrixes=False,
    num_faces=1,
    min_face_detection_confidence=0.5,
    min_face_presence_confidence=0.5,
    min_tracking_confidence=0.5
)

# สร้าง FaceLandmarker
detector = vision.FaceLandmarker.create_from_options(options)

# landmark indices สำหรับดวงตา
RIGHT_EYE = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]
LEFT_EYE = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]

# เปิดกล้อง
webcam = cv2.VideoCapture(0)

# ตัวนับเฟรมที่ตาหลับ
drowsy_frames = 0

# เก็บค่าความสูงสูงสุดของแต่ละดวงตา
max_left = 0
max_right = 0

while True:
    # อ่านภาพจากกล้อง
    ret, frame = webcam.read()
    if not ret:
        break
    
    # พลิกและแปลงภาพ
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img_h, img_w = frame.shape[:2]
    
    # แปลงเป็น MediaPipe Image
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
    
    # ประมวลผลด้วย FaceLandmarker
    detection_result = detector.detect(mp_image)
    
    # ตรวจสอบว่าพบใบหน้าหรือไม่
    if detection_result.face_landmarks:
        
        # เก็บพิกัด [x,y] ของจุดสำคัญทั้งหมดบนใบหน้า
        all_landmarks = np.array([[int(p.x * img_w), int(p.y * img_h)] 
                                 for p in detection_result.face_landmarks[0]])
            
        # วาดจุดสำคัญทั้งหมดบนใบหน้า (478 จุด)
        for landmark in all_landmarks:
            cv2.circle(frame, tuple(landmark), 1, (0, 255, 255), -1)
        
        # แยกพิกัดของดวงตาซ้ายและขวา
        right_eye = all_landmarks[RIGHT_EYE]
        left_eye = all_landmarks[LEFT_EYE]
        
        # วาดเส้นรอบดวงตาเป็นสีเขียว
        cv2.polylines(frame, [left_eye], True, (0, 255, 0), 2, cv2.LINE_AA)
        cv2.polylines(frame, [right_eye], True, (0, 255, 0), 2, cv2.LINE_AA)
        
        # วาดจุดสำคัญของดวงตาเป็นสีแดง
        for point in left_eye:
            cv2.circle(frame, tuple(point), 2, (0, 0, 255), -1)
        for point in right_eye:
            cv2.circle(frame, tuple(point), 2, (0, 0, 255), -1)
        
        # คำนวณความสูงของดวงตา
        len_left = open_len(left_eye)
        len_right = open_len(right_eye)
        
        # เก็บค่าความสูงสูงสุดของแต่ละดวงตา
        if len_left > max_left:
            max_left = len_left
        
        if len_right > max_right:
            max_right = len_right
        
        # แสดงค่าความสูงของดวงตาบนหน้าจอ
        cv2.putText(img=frame, text='Max: ' + str(max_left) + ' Left Eye: ' + str(len_left),
                   fontFace=0, org=(10, 30), fontScale=0.5, color=(0, 255, 0))
        cv2.putText(img=frame, text='Max: ' + str(max_right) + ' Right Eye: ' + str(len_right),
                   fontFace=0, org=(10, 50), fontScale=0.5, color=(0, 255, 0))
        
        # เช็คว่าตาหลับหรือไม่ (ตาหลับถ้าความสูงน้อยกว่าครึ่งหนึ่งของค่าสูงสุด)
        if (len_left <= int(max_left/2)+1 and len_right <= int(max_right/2)+1):
            drowsy_frames += 1
        else:
            drowsy_frames = 0
        
        # ถ้าตาหลับเกิน 20 เฟรม แสดงว่าง่วงนอน
        if (drowsy_frames > 20):
            cv2.putText(img=frame, text='ALERT', fontFace=0, org=(200, 300), 
                       fontScale=3, color=(0, 255, 0), thickness=3)
    
    # แสดงภาพ
    cv2.imshow('Drowsiness Detection', frame)
    
    # กด ESC เพื่อออก
    k = cv2.waitKey(1)
    if k == 27:
        break

# ปิดกล้องและหน้าต่าง
webcam.release()
cv2.destroyAllWindows()
