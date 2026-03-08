import pyautogui
from PIL import ImageGrab

logical_w, logical_h = pyautogui.size()
screenshot = ImageGrab.grab()
physical_w, physical_h = screenshot.size

print(f"Logical: {logical_w}x{logical_h}")
print(f"Physical: {physical_w}x{physical_h}")
print(f"Scaling Factor: {physical_w / logical_w}")
