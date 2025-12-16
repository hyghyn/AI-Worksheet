from PIL import Image
import pytesseract

pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe' # Update this path as needed    

image_path = 'path_to_image_th.jpg'
image = Image.open(image_path)
text = pytesseract.image_to_string(image,lang='tha+eng')

print(text)