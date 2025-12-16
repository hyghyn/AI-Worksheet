import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

BG_COLOR = (192, 192, 192)  # gray
MASK_COLOR = (255, 255, 255)  # white

# Create the options that will be used for ImageSegmenter
base_options = python.BaseOptions(model_asset_path='deeplab_v3.tflite')
options = vision.ImageSegmenterOptions(base_options=base_options,
                                       output_category_mask=True)

# Create the image segmenter
with vision.ImageSegmenter.create_from_options(options) as segmenter:
    webcam = cv2.VideoCapture(0)
    
    while True:
        success, image = webcam.read()
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        cv2.imshow("real", image)
        
        # Create the MediaPipe image file that will be segmented
        image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)
        # Retrieve the masks for the segmented image
        segmentation_result = segmenter.segment(image)
        category_mask = segmentation_result.category_mask
        
        # Generate solid color images for showing the output segmentation mask
        image_data = image.numpy_view()
        fg_image = np.zeros(image_data.shape, dtype=np.uint8)
        fg_image[:] = MASK_COLOR
        bg_image = np.zeros(image_data.shape, dtype=np.uint8)
        bg_image[:] = BG_COLOR
        
        condition = np.stack((category_mask.numpy_view(),) * 3, axis=-1) > 0.2
        output_image = np.where(condition, fg_image, bg_image)
        
        cv2.imshow("segment", output_image)
        
        k = cv2.waitKey(1)
        if k == 27:
            break
    
    cv2.destroyAllWindows()