import time
import keyboard
import pyautogui

time.sleep(2)

while True:
    if keyboard.is_pressed('q'):
        break
    try:
        start = pyautogui.locateCenterOnScreen('images.jpg',
                                               region=(0, 0, 1920, 1080),
                                               grayscale=False,
                                               confidence=0.70)
        print("Found")
        if start is not None:
            pyautogui.moveTo(start)  # Move mouse
            pyautogui.click()        # Click mouse
    except pyautogui.ImageNotFoundException:
        print("Image not found")