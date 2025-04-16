import cv2
import numpy as np
import re
import os
import sys
import logging
import traceback
from logging.handlers import RotatingFileHandler

# Configure logging
logger = logging.getLogger('plate_recognizer')
logger.setLevel(logging.INFO)

# Console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(console_handler)

# Safe logging function for handling Vietnamese characters
def safe_log(msg, level=logging.INFO):
    try:
        logger.log(level, msg)
    except UnicodeEncodeError:
        safe_msg = msg.encode('ascii', 'replace').decode('ascii')
        logger.log(level, safe_msg)
    except Exception as e:
        logger.log(logging.ERROR, f"Logging error: {str(e)}")

class LicensePlateRecognizer:
    def __init__(self):
        self.ocr_available = False
        self.tesseract_available = False
        self.reader = None
        
        # Try to load EasyOCR
        try:
            import io
            original_stdout = sys.stdout
            original_stderr = sys.stderr
            sys.stdout = io.StringIO()
            sys.stderr = io.StringIO()
            
            try:
                os.environ['EASYOCR_DISABLE_PROGRESS_BAR'] = 'True'
                
                import easyocr
                safe_log("Initializing EasyOCR. This may take a moment...")
                self.reader = easyocr.Reader(['en', 'vi'], gpu=False, verbose=False)
                self.ocr_available = True
                safe_log("EasyOCR successfully loaded")
            finally:
                captured_output = sys.stdout.getvalue()
                captured_error = sys.stderr.getvalue()
                sys.stdout = original_stdout
                sys.stderr = original_stderr
                
                if captured_error and 'error' in captured_error.lower():
                    safe_log(f"EasyOCR initialization warnings: {captured_error}", logging.WARNING)
                
        except ImportError as e:
            safe_log("EasyOCR not available. Using fallback recognition methods", logging.WARNING)
        except Exception as e:
            safe_log(f"Error initializing EasyOCR: {str(e)}", logging.ERROR)
            
        # Try to load Tesseract as fallback
        try:
            import pytesseract
            self.tesseract_available = True
            self.pytesseract = pytesseract
            safe_log("Tesseract OCR successfully loaded")
        except ImportError:
            self.tesseract_available = False
            safe_log("Tesseract OCR not available", logging.WARNING)
        
        # Simplified regex patterns for Vietnamese license plates
        self.plate_patterns = [
            # Car plates - Standard and new formats
            r'\d{2}[A-Z]-\d{3}\.\d{2}',      # 29A-123.45
            r'\d{2}[A-Z] \d{3}\.\d{2}',      # 30G 535.07
            r'\d{2}[A-Z]-\d{4}',             # 29A-1234
            r'\d{2}[A-Z] \d{4}',             # 29A 1234
            r'\d{2}[A-Z]\d{4}',              # 29A1234
            
            # Special plates formats
            r'\d{2}-[A-Z]\d \d{3}\.\d{2}',   # 29-C1 999.99
            r'\d{2}-[A-Z]{2}\d \d{3}\.\d{2}', # 17-MD7 999.99
            
            # Motorcycle plates
            r'\d{2}-[A-Z]\d \d{3}\.\d{2}',   # 59-Y3 577.77
            r'\d{2}[A-Z]\d-\d{3}\.\d{2}',    # 59Y1-999.99
            r'\d{2}-[A-Z]\d \d{5}',          # 59-Y1 99999
            
            # Plates with national flag
            r'\d{2}[A-Z] \d{3}\.\d{2}',      # 30G 535.07
            r'\d{2}[A-Z]\d{3}\.\d{2}',       # 30G535.07
            
            # Handle plates without dots
            r'\d{2}[A-Z]\d{5}',              # 30G53507
            r'\d{2}-[A-Z]\d \d{5}',          # 29-C1 99999
        ]
        
        # Province codes dictionary
        self.province_codes = {
            "11": "Cao Bằng", "12": "Lạng Sơn", "14": "Quảng Ninh", "15": "Hải Phòng",
            "16": "Hải Phòng", "17": "Thái Bình", "18": "Nam Định", "19": "Phú Thọ",
            "20": "Thái Nguyên", "21": "Yên Bái", "22": "Tuyên Quang", "23": "Hà Giang",
            "24": "Lào Cai", "25": "Lai Châu", "26": "Sơn La", "27": "Điện Biên",
            "28": "Hòa Bình", "29": "Hà Nội", "30": "Hà Nội", "31": "Hà Nội",
            "32": "Hà Nội", "33": "Hà Nội", "34": "Hải Dương", "35": "Ninh Bình",
            "36": "Thanh Hóa", "37": "Nghệ An", "38": "Hà Tĩnh", "43": "Đà Nẵng",
            "47": "Đắk Lắk", "48": "Đắk Nông", "49": "Lâm Đồng", "50": "TPHCM",
            "51": "TPHCM", "52": "TPHCM", "53": "TPHCM", "54": "TPHCM",
            "55": "TPHCM", "56": "TPHCM", "57": "TPHCM", "58": "TPHCM",
            "59": "TPHCM", "60": "Đồng Nai", "61": "Bình Dương", "62": "Long An",
            "63": "Tiền Giang", "64": "Vĩnh Long", "65": "Cần Thơ", "66": "Đồng Tháp",
            "67": "An Giang", "68": "Kiên Giang", "69": "Cà Mau", "70": "Tây Ninh",
            "71": "Bến Tre", "72": "Bà Rịa - Vũng Tàu", "73": "Quảng Bình",
            "74": "Quảng Trị", "75": "Thừa Thiên Huế", "76": "Quảng Ngãi",
            "77": "Bình Định", "78": "Phú Yên", "79": "Khánh Hòa", "80": "Gia Lai"
        }
        
        # Configuration parameters
        self.min_plate_area = 500        # Minimum size of license plate
        self.max_plate_area = 100000     # Maximum size of license plate
        self.min_plate_ratio = 0.8       # Min width/height ratio
        self.max_plate_ratio = 10.0      # Max width/height ratio
        self.min_ocr_confidence = 0.15   # Min confidence threshold for OCR
        self.min_valid_confidence = 0.3  # Min confidence for valid results

    def preprocess_image(self, image):
        """Preprocess the image with multiple methods to enhance license plate recognition"""
        # Check image size and resize if needed
        h, w = image.shape[:2]
        
        if w > 1200:
            scale = 1200 / w
            new_size = (int(w * scale), int(h * scale))
            image = cv2.resize(image, new_size, interpolation=cv2.INTER_AREA)
            safe_log(f"Image resized from {w}x{h} to {new_size[0]}x{new_size[1]}")
        
        # Store processed images in a dictionary
        results = {}
        
        # 1. Basic grayscale conversion
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image.copy()
        results['gray'] = gray
        
        # 2. Histogram equalization
        gray_eq = cv2.equalizeHist(gray)
        results['gray_eq'] = gray_eq
        
        # 3. CLAHE - Contrast Limited Adaptive Histogram Equalization
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        gray_clahe = clahe.apply(gray)
        results['gray_clahe'] = gray_clahe
        
        # 4. Denoising filters
        blur = cv2.bilateralFilter(gray_clahe, 11, 17, 17)  # Better edge preservation
        results['blur'] = blur
        
        gaussian_blur = cv2.GaussianBlur(gray_clahe, (5, 5), 0)
        results['gaussian_blur'] = gaussian_blur
        
        # 5. Edge detection methods
        edges = cv2.Canny(blur, 100, 200)
        results['edges'] = edges
        
        # 6. Thresholding methods
        _, thresh_otsu = cv2.threshold(gray_clahe, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        results['thresh_otsu'] = thresh_otsu
        
        _, thresh_otsu_inv = cv2.threshold(gray_clahe, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        results['thresh_otsu_inv'] = thresh_otsu_inv
        
        # 7. Adaptive thresholding
        adaptive_thresh = cv2.adaptiveThreshold(gray_clahe, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                                cv2.THRESH_BINARY, 11, 2)
        results['adaptive_thresh'] = adaptive_thresh
        
        # 8. Morphological operations
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        
        morph_close = cv2.morphologyEx(thresh_otsu, cv2.MORPH_CLOSE, kernel, iterations=2)
        results['morph_close'] = morph_close
        
        # 9. Special processing for national flag plates
        if len(image.shape) == 3:
            # Convert to LAB color space to enhance contrast
            lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            clahe_lab = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
            l = clahe_lab.apply(l)
            lab = cv2.merge((l, a, b))
            enhanced_lab = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
            results['enhanced_lab'] = cv2.cvtColor(enhanced_lab, cv2.COLOR_BGR2GRAY)
            
            # Increase contrast and brightness
            alpha = 1.5  # Contrast factor
            beta = 20    # Brightness
            contrast_bright = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)
            results['contrast_bright'] = cv2.cvtColor(contrast_bright, cv2.COLOR_BGR2GRAY)
        
        # Store original image for visualization
        results['original'] = image
        
        return results
    
    def find_plate_contours(self, processed_images, original_image):
        """Find contours that are likely to be license plates"""
        contour_results = []
        h_img, w_img = original_image.shape[:2]
        
        # List of binary images to find contours
        binary_images = [
            ('morph_close', processed_images.get('morph_close')),
            ('thresh_otsu', processed_images.get('thresh_otsu')),
            ('thresh_otsu_inv', processed_images.get('thresh_otsu_inv')),
            ('adaptive_thresh', processed_images.get('adaptive_thresh')),
            ('edges', processed_images.get('edges')),
            ('contrast_bright', processed_images.get('contrast_bright')),
            ('enhanced_lab', processed_images.get('enhanced_lab'))
        ]
        
        # Find contours from each processed image
        for img_name, image_to_process in binary_images:
            if image_to_process is None or len(image_to_process.shape) > 2 or image_to_process.dtype != np.uint8:
                continue
                
            # Find all contours
            contours, hierarchy = cv2.findContours(image_to_process, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            
            # Sort contours by area (largest first) and take top 30
            contours = sorted(contours, key=cv2.contourArea, reverse=True)[:30]
            
            for i, cnt in enumerate(contours):
                # Calculate perimeter and area
                peri = cv2.arcLength(cnt, True)
                area = cv2.contourArea(cnt)
                
                # Skip tiny contours
                if area < self.min_plate_area:
                    continue
                
                # Approximate polygon
                approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
                
                # Get bounding rectangle
                x, y, w, h = cv2.boundingRect(approx)
                rect_area = w * h
                ratio = float(w) / float(h)
                
                # Check basic conditions for license plates
                if 4 <= len(approx) <= 10:  # Reasonable polygon vertices
                    if (self.min_plate_ratio <= ratio <= self.max_plate_ratio and 
                        self.min_plate_area <= rect_area <= self.max_plate_area):
                        
                        # Calculate score based on plate properties
                        score = self.calculate_contour_score(approx, x, y, w, h, area, ratio, original_image)
                        
                        # Increase score for flag-based plates
                        if img_name in ['contrast_bright', 'enhanced_lab']:
                            score += 5
                            
                        contour_results.append({
                            'contour': cnt,
                            'approx': approx,
                            'bbox': (x, y, w, h),
                            'area': area,
                            'ratio': ratio,
                            'score': score,
                            'source': img_name
                        })
        
        # Filter duplicate contours
        unique_contours = self.filter_duplicate_contours(contour_results)
        
        # Sort by score and return best contours
        unique_contours.sort(key=lambda x: x['score'], reverse=True)
        
        return [(c['contour'], c['approx'], c['bbox']) for c in unique_contours[:10]]
    
    def calculate_contour_score(self, approx, x, y, w, h, area, ratio, original_image):
        """Calculate a score for how likely a contour is to be a license plate"""
        score = 0
        h_img, w_img = original_image.shape[:2]
        
        # 1. Width/height ratio
        if 3.5 <= ratio <= 5.5:  # Car plates (horizontal)
            score += 20
        elif 0.6 <= ratio <= 0.9:  # Motorcycle plates (vertical)
            score += 15
        elif 1.8 <= ratio <= 3.0:  # Special plates
            score += 10
        
        # 2. Position in image
        # Plates are usually in the middle or lower part of the image
        center_y = y + h/2
        if center_y > h_img * 0.4:
            position_score = min(10, (center_y / h_img) * 10)
            score += position_score
        
        # 3. Rectangle similarity
        rect_area = w * h
        # Higher score for contours that closely resemble rectangles
        if rect_area > 0 and area / rect_area > 0.7:
            score += 15
        
        # 4. Number of vertices in approximated polygon
        # License plates should approximate to rectangles (4 vertices)
        vertex_score = 10 - min(abs(len(approx) - 4) * 1.5, 9)
        score += vertex_score
        
        # 5. Relative area
        area_ratio = rect_area / (w_img * h_img)
        if 0.01 <= area_ratio <= 0.2:
            score += 10 * (1 - abs(area_ratio - 0.05) / 0.2)
        
        return score

    def filter_duplicate_contours(self, contour_results):
        """Remove duplicate or overlapping contours"""
        if not contour_results:
            return []
            
        unique_contours = []
        used_indices = set()
        
        # Sort by score (highest first)
        sorted_contours = sorted(contour_results, key=lambda x: x['score'], reverse=True)
        
        for i, contour in enumerate(sorted_contours):
            if i in used_indices:
                continue
                
            x, y, w, h = contour['bbox']
            current_rect = (x, y, x + w, y + h)
            unique_contours.append(contour)
            
            # Mark similar contours
            for j, other_contour in enumerate(sorted_contours):
                if j in used_indices or i == j:
                    continue
                    
                ox, oy, ow, oh = other_contour['bbox']
                other_rect = (ox, oy, ox + ow, oy + oh)
                
                # Calculate IoU (Intersection over Union)
                intersection_area = max(0, min(current_rect[2], other_rect[2]) - max(current_rect[0], other_rect[0])) * \
                                   max(0, min(current_rect[3], other_rect[3]) - max(current_rect[1], other_rect[1]))
                
                if intersection_area == 0:
                    continue
                    
                union_area = (w * h) + (ow * oh) - intersection_area
                iou = intersection_area / union_area if union_area > 0 else 0
                
                # If IoU is large, consider them the same object
                if iou > 0.5:
                    used_indices.add(j)
        
        return unique_contours
    
    def extract_plate_regions(self, image, possible_plates):
        """Extract and preprocess license plate regions from the image"""
        plate_regions = []
        
        for cnt, approx, (x, y, w, h) in possible_plates:
            # Add small margin around the plate
            margin = int(min(w, h) * 0.03)
            y_start = max(0, y - margin)
            y_end = min(image.shape[0], y + h + margin)
            x_start = max(0, x - margin)
            x_end = min(image.shape[1], x + w + margin)
            
            # Crop plate region from original image
            plate_img = image[y_start:y_end, x_start:x_end]
            
            # Skip if region is too small
            if plate_img.size == 0 or plate_img.shape[0] == 0 or plate_img.shape[1] == 0:
                continue
            
            # Create dictionary for this plate region
            plate_region = {'bbox': (x, y, w, h), 'original': plate_img}
            
            # Process plate region with various methods
            
            # 1. Convert to grayscale
            plate_gray = cv2.cvtColor(plate_img, cv2.COLOR_BGR2GRAY) if len(plate_img.shape) == 3 else plate_img
            plate_region['gray'] = plate_gray
            
            # 2. Apply CLAHE for better contrast
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            plate_clahe = clahe.apply(plate_gray)
            plate_region['clahe'] = plate_clahe
            
            # 3. Apply Gaussian blur to reduce noise
            plate_blur = cv2.GaussianBlur(plate_clahe, (5, 5), 0)
            plate_region['blur'] = plate_blur
            
            # 4. Apply binary thresholding
            _, plate_thresh = cv2.threshold(plate_clahe, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            plate_region['thresh'] = plate_thresh
            
            _, plate_thresh_inv = cv2.threshold(plate_clahe, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            plate_region['thresh_inv'] = plate_thresh_inv
            
            # 5. Apply adaptive thresholding
            plate_adaptive = cv2.adaptiveThreshold(plate_clahe, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                                 cv2.THRESH_BINARY, 11, 2)
            plate_region['adaptive'] = plate_adaptive
            
            # 6. Enhance edges with morphological operations
            kernel = np.ones((2, 2), np.uint8)
            plate_open = cv2.morphologyEx(plate_thresh_inv, cv2.MORPH_OPEN, kernel, iterations=1)
            plate_region['open'] = plate_open
            
            # 7. Sharpen the image
            sharp_kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
            plate_sharp = cv2.filter2D(plate_clahe, -1, sharp_kernel)
            plate_region['sharp'] = plate_sharp
            
            # 8. Special processing for plates with flag
            # Increase contrast dramatically
            alpha = 2.0  # Contrast factor
            beta = 50    # Brightness
            plate_contrast = cv2.convertScaleAbs(plate_gray, alpha=alpha, beta=beta)
            plate_region['contrast'] = plate_contrast
            
            # Add to the results list
            plate_regions.append(plate_region)
        
        return plate_regions

    def recognize_text_easyocr(self, image, allowlist=None):
        """Recognize text using EasyOCR with optimized configuration"""
        if not self.ocr_available:
            return None
        
        try:
            # Resize small images to improve recognition
            h, w = image.shape[:2]
            if max(h, w) < 200:
                image = cv2.resize(image, (w*2, h*2), interpolation=cv2.INTER_CUBIC)
            
            # Set allowlist for Vietnamese license plates
            if allowlist is None:
                allowlist = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ-. "
            
            # Redirect stdout/stderr to prevent encoding errors
            import io
            original_stdout = sys.stdout
            original_stderr = sys.stderr
            sys.stdout = io.StringIO()
            sys.stderr = io.StringIO()
            
            try:
                # Optimize parameters for license plate recognition
                results = self.reader.readtext(
                    image, 
                    paragraph=False,
                    detail=1,
                    allowlist=allowlist,
                    contrast_ths=0.1,
                    adjust_contrast=0.5,
                    text_threshold=0.3,
                    link_threshold=0.3,
                    add_margin=0.1,
                    width_ths=0.5,
                    height_ths=0.5,
                    blocklist="*&@#$%^()_+={}[]|\\:;<>?~/",
                    batch_size=4,
                    mag_ratio=1.5
                )
            finally:
                # Restore stdout/stderr
                sys.stdout = original_stdout
                sys.stderr = original_stderr
            
            # Process the results
            texts = []
            for (bbox, text, prob) in results:
                if prob > self.min_ocr_confidence:
                    texts.append((text, prob, bbox))
            
            # Sort by confidence (highest first)
            texts.sort(key=lambda x: x[1], reverse=True)
            
            return texts
        except Exception as e:
            safe_log(f"EasyOCR error: {str(e)}", logging.ERROR)
            return None

    def recognize_text_tesseract(self, image):
        """Recognize text using Tesseract OCR as a fallback"""
        if not self.tesseract_available:
            return None
        
        try:
            # Try different Tesseract configurations
            configs = [
                r'--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-.',
                r'--oem 3 --psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-.',
                r'--oem 3 --psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-.'
            ]
            
            results = []
            
            for config in configs:
                text = self.pytesseract.image_to_string(image, config=config)
                
                if text:
                    # Clean the text
                    cleaned_text = re.sub(r'[^A-Z0-9\-\.]', '', text.upper())
                    if cleaned_text:
                        # Get confidence data if available
                        try:
                            data = self.pytesseract.image_to_data(image, config=config, output_type=self.pytesseract.Output.DICT)
                            if data['conf'] and len(data['conf']) > 0:
                                confidences = [float(conf) for conf in data['conf'] if conf != '-1']
                                avg_conf = sum(confidences) / len(confidences) if confidences else 70.0
                                # Normalize to 0-1 scale like EasyOCR
                                norm_conf = avg_conf / 100.0
                                results.append((cleaned_text, norm_conf))
                            else:
                                results.append((cleaned_text, 0.7))
                        except:
                            results.append((cleaned_text, 0.7))
            
            # Sort by confidence
            results.sort(key=lambda x: x[1], reverse=True)
            return results if results else None
            
        except Exception as e:
            safe_log(f"Tesseract OCR error: {str(e)}", logging.ERROR)
            return None

    def validate_plate_number(self, text):
        """Validate and format the license plate text"""
        if not text:
            return False, "", 0
        
        # Remove unnecessary characters, keep only letters, numbers, dots, hyphens, and spaces
        cleaned_text = re.sub(r'[^\w\.\-\s]', '', text)
        
        # Convert to uppercase
        cleaned_text = cleaned_text.upper()
        
        # Check if it matches any known plate pattern
        for pattern in self.plate_patterns:
            if re.search(pattern, cleaned_text, re.IGNORECASE):
                return True, cleaned_text, 1.0
        
        # Try to correct common OCR errors
        corrected_text = self.correct_ocr_errors(cleaned_text)
        
        # Check again with corrected text
        for pattern in self.plate_patterns:
            if re.search(pattern, corrected_text, re.IGNORECASE):
                return True, corrected_text, 0.9
        
        # If still no match, assume it might be a valid plate and return
        return True, corrected_text, 0.7

    def correct_ocr_errors(self, text):
        """Correct common OCR errors in license plate text"""
        if not text:
            return text
            
        # Common OCR substitutions
        corrections = {
            'O': '0', 'I': '1', 'l': '1', 'L': '1',
            'B': '8', 'S': '5', 'Z': '2', 'G': '6',
            'D': '0', 'Q': '0', 'T': '7'
        }
        
        # Apply contextual corrections
        corrected_text = text
        
        # Process each character
        for i, char in enumerate(text):
            # First two positions are usually numbers (province code)
            if i < 2 and char in 'OQDB':
                corrected_text = corrected_text.replace(char, '0', 1)
            # Third position is usually a letter (in 29A, 30G, etc.)
            elif i == 2 and char in '0123456789':
                letter_map = {'0': 'O', '1': 'I', '4': 'A', '6': 'G', '8': 'B'}
                if char in letter_map:
                    corrected_text = corrected_text[:i] + letter_map[char] + corrected_text[i+1:]
            # Rest are usually numbers or separators
            elif i > 2 and char in 'OQDBSZ':
                number_map = {'O': '0', 'Q': '0', 'D': '0', 'B': '8', 'S': '5', 'Z': '2'}
                if char in number_map:
                    corrected_text = corrected_text[:i] + number_map[char] + corrected_text[i+1:]
        
        return corrected_text

    def format_plate_text(self, text):
        """Format the text into a standard string format with no separators"""
        if not text:
            return text
            
        # Remove all non-alphanumeric characters (spaces, dashes, dots)
        clean_text = re.sub(r'[^A-Z0-9]', '', text.upper())
        
        # Special handling for national flag plates (with VIE)
        clean_text = clean_text.replace('VIE', '')
        
        return clean_text

    def detect_flag(self, image):
        """Detect if the license plate has a Vietnamese flag"""
        try:
            # Convert to HSV to easily detect red color
            if len(image.shape) == 3:  # Color image
                hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
                
                # Red color range in HSV
                lower_red1 = np.array([0, 100, 100])
                upper_red1 = np.array([10, 255, 255])
                mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
                
                lower_red2 = np.array([160, 100, 100])
                upper_red2 = np.array([180, 255, 255])
                mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
                
                # Combine the two red ranges
                red_mask = cv2.bitwise_or(mask1, mask2)
                
                # Count red pixels
                red_pixels = np.sum(red_mask > 0)
                
                # If enough red pixels are found, and mostly on the left side
                if red_pixels > 500:
                    h, w = image.shape[:2]
                    left_half_mask = red_mask[:, :w//4]
                    left_red_pixels = np.sum(left_half_mask > 0)
                    
                    if left_red_pixels > red_pixels * 0.7:
                        return True
            
            return False
        except Exception as e:
            safe_log(f"Error detecting flag: {str(e)}", logging.WARNING)
            return False

    def detect_plate_from_image(self, img, output_raw=True):
        """Detect and recognize license plate from image
        
        Args:
            img: Input image
            output_raw: If True, returns the plate text without formatting (no spaces/dots)
                        If False, returns the original detected text
        
        Returns:
            tuple: (plate_text, result_image)
        """
        try:
            result_image = img.copy()
            
            # Preprocess the image
            processed_images = self.preprocess_image(img)
            
            # Find possible plate contours
            possible_plates = self.find_plate_contours(processed_images, img)
            
            # If no suitable contours found, try direct OCR on the whole image
            if not possible_plates:
                safe_log("No suitable license plate contours found", logging.WARNING)
                
                if self.ocr_available:
                    has_flag = self.detect_flag(img)
                    
                    # If flag detected, increase likelihood this is a plate image
                    allowlist = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ-."
                    text_results = self.recognize_text_easyocr(img, allowlist)
                    
                    if text_results:
                        for text, prob, bbox in text_results:
                            valid, validated_text, confidence = self.validate_plate_number(text)
                            if valid:
                                safe_log(f"Direct recognition found plate: {validated_text}")
                                
                                # Draw the detection on result image
                                try:
                                    bbox_points = np.array(bbox).astype(np.int32).reshape((-1, 1, 2))
                                    cv2.polylines(result_image, [bbox_points], True, (0, 255, 0), 2)
                                    cv2.putText(result_image, validated_text, (int(bbox[0][0]), int(bbox[0][1]) - 10), 
                                              cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                                except:
                                    pass
                                
                                # Return either raw or formatted text
                                if output_raw:
                                    return self.format_plate_text(validated_text), result_image
                                else:
                                    return validated_text, result_image
                
                return None, result_image
            
            # Draw contours on result image
            for contour, _, _ in possible_plates:
                cv2.drawContours(result_image, [contour], -1, (0, 255, 0), 2)
            
            # Extract plate regions
            plate_regions = self.extract_plate_regions(img, possible_plates)
            
            # List to store all valid results
            all_results = []
            
            # Try to recognize text in each plate region
            for i, plate_region in enumerate(plate_regions):
                region_results = []
                
                # Check if plate has flag
                has_flag = self.detect_flag(plate_region['original'])
                flag_bonus = 0.1 if has_flag else 0.0  # Bonus score for plates with flag
                
                # Image types in order of preference
                image_types = [
                    'clahe', 'adaptive', 'thresh',
                    'thresh_inv', 'sharp', 'contrast',
                    'gray', 'original'
                ]
                
                # Try EasyOCR first
                if self.ocr_available:
                    allowlist = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ-. "
                    
                    for img_type in image_types:
                        if img_type in plate_region:
                            text_results = self.recognize_text_easyocr(plate_region[img_type], allowlist)
                            
                            if text_results:
                                for text, prob, _ in text_results:
                                    valid, validated_text, extra_conf = self.validate_plate_number(text)
                                    
                                    if valid:
                                        # Calculate combined confidence score
                                        final_conf = prob * extra_conf + flag_bonus
                                        region_results.append((validated_text, final_conf, "easyocr", img_type))
                
                # Try Tesseract as fallback
                if self.tesseract_available and (not region_results or len(region_results) < 2):
                    for img_type in image_types:
                        if img_type in plate_region:
                            text_results = self.recognize_text_tesseract(plate_region[img_type])
                            
                            if text_results:
                                for text, prob in text_results:
                                    valid, validated_text, extra_conf = self.validate_plate_number(text)
                                    
                                    if valid:
                                        final_conf = prob * extra_conf + flag_bonus
                                        region_results.append((validated_text, final_conf, "tesseract", img_type))
                
                # If we have results for this region
                if region_results:
                    # Sort by confidence
                    region_results.sort(key=lambda x: x[1], reverse=True)
                    best_result = region_results[0]
                    
                    # Add to overall results
                    all_results.append((best_result[0], best_result[1], plate_region['bbox']))
                    
                    # Draw bounding box around the plate
                    x, y, w, h = plate_region['bbox']
                    cv2.rectangle(result_image, (x, y), (x + w, y + h), (0, 0, 255), 2)
                    
                    # Draw the plate text
                    cv2.putText(result_image, best_result[0], (x, y - 10), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            
            # If we found any valid plates
            if all_results:
                # Sort by confidence
                all_results.sort(key=lambda x: x[1], reverse=True)
                best_plate = all_results[0][0]
                
                # Get province info if available
                province_info = ""
                if len(best_plate) >= 2 and best_plate[:2].isdigit():
                    province_code = best_plate[:2]
                    if province_code in self.province_codes:
                        province_info = self.province_codes[province_code]
                
                # Draw the best result at the top of the image
                cv2.rectangle(result_image, (5, 5), (380, 35), (0, 0, 0), -1)
                cv2.putText(result_image, best_plate, (10, 30), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                
                if province_info:
                    from PIL import ImageFont, ImageDraw, Image

                    # Chuyển từ OpenCV image (numpy) sang PIL
                    result_image_pil = Image.fromarray(cv2.cvtColor(result_image, cv2.COLOR_BGR2RGB))
                    draw = ImageDraw.Draw(result_image_pil)

                    # Dùng font Unicode (ví dụ: Arial Unicode, hoặc font Việt Unicode khác)
                    font = ImageFont.truetype("arial.ttf", 20)  # bạn có thể thay bằng đường dẫn đến font hỗ trợ tiếng Việt

                    # Vẽ chữ tỉnh
                    draw.text((220, 5), f"({province_info})", font=font, fill=(0, 255, 0))

                    # Chuyển lại về OpenCV image
                    result_image = cv2.cvtColor(np.array(result_image_pil), cv2.COLOR_RGB2BGR)

                
                # Return either raw or formatted text
                if output_raw:
                    return self.format_plate_text(best_plate), result_image
                else:
                    return best_plate, result_image
            
            # No valid results found
            return None, result_image
            
        except Exception as e:
            tb_str = "".join(traceback.format_exception(type(e), e, e.__traceback__))
            safe_log(f"Error in detect_plate_from_image: {str(e)}\n{tb_str}", logging.ERROR)
            return None, img

    def recognize_plate(self, image_path, output_raw=True):
        """Recognize license plate from an image file
        
        Args:
            image_path: Path to the image file
            output_raw: If True, returns raw text without formatting
        """
        try:
            # Read the image
            image = cv2.imread(image_path)
            if image is None:
                safe_log(f"Could not read image from {image_path}", logging.ERROR)
                return None, None
            
            safe_log(f"Processing image: {image_path}")
            
            # Detect plate from the image
            plate_number, result_image = self.detect_plate_from_image(image, output_raw)
            
            # Return the results
            if plate_number:
                safe_log(f"Successfully recognized license plate: {plate_number}")
                return plate_number, result_image
            else:
                safe_log("No license plate found in the image")
                return None, result_image
            
        except Exception as e:
            tb_str = "".join(traceback.format_exception(type(e), e, e.__traceback__))
            safe_log(f"Error processing license plate image: {str(e)}\n{tb_str}", logging.ERROR)
            return None, None

    def process_image(self, image_path, output_raw=True):
        """Process image and return license plate text"""
        return self.recognize_plate(image_path, output_raw)
        
    def process_multiple_images(self, image_paths, output_dir=None, output_raw=True):
        """Process multiple images and optionally save results
        
        Args:
            image_paths: List of image file paths
            output_dir: Directory to save result images (optional)
            output_raw: If True, returns raw text without formatting
        """
        results = []
        
        for image_path in image_paths:
            plate_number, result_image = self.recognize_plate(image_path, output_raw)
            
            results.append({
                'image_path': image_path,
                'plate_number': plate_number
            })
            
            # Save result image if output directory provided
            if output_dir and result_image is not None:
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)
                
                filename = os.path.basename(image_path)
                output_path = os.path.join(output_dir, f"result_{filename}")
                cv2.imwrite(output_path, result_image)
                results[-1]['result_image'] = output_path
        
        return results