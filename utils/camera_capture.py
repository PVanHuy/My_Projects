import cv2
import os
from datetime import datetime

def capture_image(save_dir):
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise IOError("Không mở được camera")

    ret, frame = cap.read()
    cap.release()

    if not ret:
        raise IOError("Không thể chụp ảnh")

    filename = datetime.now().strftime("plate_%Y%m%d_%H%M%S.jpg")
    path = os.path.join(save_dir, filename)
    cv2.imwrite(path, frame)
    return path, frame