import sys
import os
from recognition.license_plate_recognizer import LicensePlateRecognizer

# Đảm bảo thư mục recognition có thể được import
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
recognition_dir = os.path.join(parent_dir, 'recognition')
if recognition_dir not in sys.path:
    sys.path.append(recognition_dir)

# Tạo instance của recognizer
recognizer = LicensePlateRecognizer()

def recognize_license_plate(image_path):
    """
    Recognizes a license plate from an image file.
    
    Args:
        image_path (str): Path to the license plate image
        
    Returns:
        str: Recognized license plate number or empty string if none found
    """
    # Kiểm tra file có tồn tại không
    if not os.path.exists(image_path):
        return ""
    
    # Sử dụng recognizer để nhận diện biển số
    plate_number, _ = recognizer.recognize_plate(image_path)
    
    if plate_number:
        return plate_number
    else:
        return ""


def process_license_plate_image(image_path):
    """
    Processes a license plate image to enhance recognition.
    
    Args:
        image_path (str): Path to the license plate image
        
    Returns:
        numpy.ndarray: Processed image or None if processing failed
    """
    # Kiểm tra file có tồn tại không
    if not os.path.exists(image_path):
        return None
    
    # Sử dụng recognizer để xử lý ảnh và trả về kết quả
    _, processed_image = recognizer.recognize_plate(image_path)
    
    return processed_image