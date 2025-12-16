import numpy as np
import pandas as pd
import PIL
import tensorflow as tf
import tensorflow_hub as hub

model_url = 'https://tfhub.dev/google/on_device_vision/classifier/landmarks_classifier_asia_V1/1'
labels = 'landmarks_asia_label_map.csv'
img_shape = (321, 321)
classifier = tf.keras.Sequential([hub.KerasLayer(model_url, input_shape=img_shape+(3,), output_key="predictions:logits")])

df = pd.read_csv(labels)
labels = dict(zip(df.id, df.name))

def landmark_detection(image_path):
    img = PIL.Image.open(image_path)
    img = img.resize(img_shape)
    img = np.array(img)/255.0
    img = img[np.newaxis, :]
    result = classifier.predict(img)
    # show top 1 landmark
    # print(labels[np.argmax(result)])
    # show top 5 landmarks
    top5 = np.argsort(result[0])[::-1][:5]
    for i in top5:
        print(labels[i], result[0][i])

landmark_detection('test_image.jpg')  # เปลี่ยนชื่อไฟล์ตามต้องการ
