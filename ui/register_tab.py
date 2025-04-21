# ui/register_tab.py
from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QFileDialog,
    QMessageBox, QFrame, QGroupBox, QFormLayout, QSplitter, QWidget,
    QComboBox, QCompleter, QGraphicsDropShadowEffect, QGridLayout, QScrollArea
)
from PyQt5.QtGui import QPixmap, QImage, QFont, QIcon, QColor
from PyQt5.QtCore import Qt, QTimer, QSize

from colors.my_colors import MyColor
from ui.style import setup_animation, create_title_label, create_styled_button
from utils.app_icons import AppIcons
from utils.plate_recognition import recognize_license_plate, process_license_plate_image
from database.db_manager import DatabaseManager
import logging

# Cấu hình logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def setup_register_tab(tab, main_window):
    """Set up the registration tab with form and license plate recognition"""
    # Tạo layout chính cho tab
    main_layout = QVBoxLayout(tab)
    main_layout.setContentsMargins(0, 0, 0, 0)
    
    # Tạo scroll area để cho phép cuộn
    scroll_area = QScrollArea()
    scroll_area.setWidgetResizable(True)
    scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
    # Tạo widget chứa nội dung
    content_widget = QWidget()
    layout = QVBoxLayout(content_widget)
    layout.setSpacing(20)
    layout.setContentsMargins(15, 15, 15, 15)  # Thêm padding vào nội dung

    # Title with icon using helper function
    title_widget = create_title_label("ĐĂNG KÝ XE MỚI", "register")
    layout.addWidget(title_widget)

    # Use splitter for better layout control
    content_splitter = QSplitter(Qt.Vertical)
    content_splitter.setChildrenCollapsible(False)
    content_splitter.setHandleWidth(8)
    content_splitter.setStyleSheet(f"""
        QSplitter::handle {{
            background-color: {MyColor.LIGHT_GRAY};
            border-radius: 4px;
        }}
    """)

    # Top widget with owner and vehicle information
    top_widget = QWidget()
    top_layout = QVBoxLayout(top_widget)
    top_layout.setContentsMargins(0, 0, 0, 0)

    # Owner information group
    owner_group = QGroupBox("Thông tin chủ xe")
    owner_group.setFont(QFont("Arial", 12, QFont.Bold))
    owner_form = QFormLayout()

    # Owner name input with validation
    if not hasattr(main_window, 'owner_name_input'):
        main_window.owner_name_input = QLineEdit()
        main_window.owner_name_input.setPlaceholderText("Nhập họ tên chủ xe")
        main_window.owner_name_input.setMinimumHeight(35)

    # Phone number input with validation
    if not hasattr(main_window, 'owner_phone_input'):
        main_window.owner_phone_input = QLineEdit()
        main_window.owner_phone_input.setPlaceholderText("Nhập số điện thoại")
        main_window.owner_phone_input.setMinimumHeight(35)
        # Add validator later if needed

    # Add fields to form
    owner_form.addRow("Họ tên:", main_window.owner_name_input)
    owner_form.addRow("Số điện thoại:", main_window.owner_phone_input)
    owner_group.setLayout(owner_form)

    # Vehicle information group
    vehicle_group = QGroupBox("Thông tin xe")
    vehicle_group.setFont(QFont("Arial", 12, QFont.Bold))
    vehicle_form = QFormLayout()

    # License plate input with validation
    if not hasattr(main_window, 'plate_input'):
        main_window.plate_input = QLineEdit()
        main_window.plate_input.setPlaceholderText("Nhập biển số xe")
        main_window.plate_input.setMinimumHeight(35)
        # Thêm validator để chỉ cho phép ký tự chữ và số, không có khoảng trắng hoặc ký tự đặc biệt
        from PyQt5.QtGui import QRegExpValidator
        from PyQt5.QtCore import QRegExp
        
        # Regex chỉ cho phép chữ cái và số
        reg_ex = QRegExp("^[A-Za-z0-9]+$")
        plate_validator = QRegExpValidator(reg_ex)
        main_window.plate_input.setValidator(plate_validator)
        
        # Kết nối sự kiện textChanged để tự động chuyển đổi sang chữ in hoa
        main_window.plate_input.textChanged.connect(lambda text: main_window.plate_input.setText(text.upper()))
    # Vehicle type dropdown with common options
    if not hasattr(main_window, 'vehicle_type_input'):
        main_window.vehicle_type_input = QComboBox()
        main_window.vehicle_type_input.addItems([
            "Xe ô tô", "Xe máy", "Xe khách", "Khác"
        ])
        main_window.vehicle_type_input.setMinimumHeight(35)

    # Brand dropdown with common manufacturers
    if not hasattr(main_window, 'brand_input'):
        main_window.brand_input = QComboBox()
        main_window.brand_input.addItems([
            "Toyota", "Honda", "Mazda", "Ford", "Hyundai", 
            "Kia", "Mercedes-Benz", "BMW", "Audi", "Chevrolet",
            "Nissan", "Mitsubishi", "Suzuki", "Yamaha", "Khác"
        ])
        main_window.brand_input.setMinimumHeight(35)

    # Color input
    if not hasattr(main_window, 'color_input'):
        main_window.color_input = QComboBox()
        main_window.color_input.addItems([
            "Trắng", "Đen", "Xám", "Bạc", "Đỏ", "Xanh dương", 
            "Xanh lá", "Vàng", "Cam", "Nâu", "Hồng", "Tím", "Khác"
        ])
        main_window.color_input.setMinimumHeight(35)
     # Province input (new)
    if not hasattr(main_window, 'province_input'):
        main_window.province_input = QComboBox()
        main_window.province_input.addItems([
            "Hà Nội", "TP Hồ Chí Minh", "Đà Nẵng", "Hải Phòng", "Cần Thơ",
            "An Giang", "Bà Rịa - Vũng Tàu", "Bắc Giang", "Bắc Kạn", "Bạc Liêu",
            "Bắc Ninh", "Bến Tre", "Bình Định", "Bình Dương", "Bình Phước",
            "Bình Thuận", "Cà Mau", "Cao Bằng", "Đắk Lắk", "Đắk Nông",
            "Điện Biên", "Đồng Nai", "Đồng Tháp", "Gia Lai", "Hà Giang",
            "Hà Nam", "Hà Tĩnh", "Hải Dương", "Hậu Giang", "Hòa Bình",
            "Hưng Yên", "Khánh Hòa", "Kiên Giang", "Kon Tum", "Lai Châu",
            "Lâm Đồng", "Lạng Sơn", "Lào Cai", "Long An", "Nam Định",
            "Nghệ An", "Ninh Bình", "Ninh Thuận", "Phú Thọ", "Phú Yên",
            "Quảng Bình", "Quảng Nam", "Quảng Ngãi", "Quảng Ninh", "Quảng Trị",
            "Sóc Trăng", "Sơn La", "Tây Ninh", "Thái Bình", "Thái Nguyên",
            "Thanh Hóa", "Thừa Thiên Huế", "Tiền Giang", "Trà Vinh", "Tuyên Quang",
            "Vĩnh Long", "Vĩnh Phúc", "Yên Bái"
        ])
        main_window.province_input.setMinimumHeight(35)
    # Notes input (new)
    if not hasattr(main_window, 'notes_input'):
        main_window.notes_input = QLineEdit()
        main_window.notes_input.setPlaceholderText("Ghi chú (không bắt buộc)")
        main_window.notes_input.setMinimumHeight(35)

    # Add fields to form
    vehicle_form.addRow("Biển số xe:", main_window.plate_input)
    vehicle_form.addRow("Loại xe:", main_window.vehicle_type_input)
    vehicle_form.addRow("Hãng xe:", main_window.brand_input)
    vehicle_form.addRow("Màu xe:", main_window.color_input)
    vehicle_form.addRow("Tỉnh/Thành phố:", main_window.province_input)
    vehicle_form.addRow("Ghi chú:", main_window.notes_input)
    vehicle_group.setLayout(vehicle_form)
    
    # Add groups to top layout
    top_layout.addWidget(owner_group)
    top_layout.addWidget(vehicle_group)

    # Bottom widget with license plate recognition
    bottom_widget = QWidget()
    bottom_layout = QVBoxLayout(bottom_widget)
    bottom_layout.setContentsMargins(0, 0, 0, 0)

    # Sử dụng phương pháp cải tiến để hiển thị phần nhận diện biển số
    setup_recognition_section(main_window, bottom_layout)

    # Add top and bottom widgets to splitter
    content_splitter.addWidget(top_widget)
    content_splitter.addWidget(bottom_widget)
    content_splitter.setSizes([300, 500])

    # Add splitter to main layout
    layout.addWidget(content_splitter)

    # Register button
    register_btn = create_styled_button("ĐĂNG KÝ XE", "save", "success", height=50)
    register_btn.setFont(QFont("Arial", 12, QFont.Bold))
    register_btn.clicked.connect(lambda: register_vehicle(main_window))
    layout.addWidget(register_btn)
    
    # Load image if there's a path stored
    if hasattr(main_window, 'original_img_path'):
        try:
            pixmap = QPixmap(main_window.original_img_path)
            if not pixmap.isNull():
                pixmap_scaled = pixmap.scaled(
                    main_window.original_img.width() - 20,
                    main_window.original_img.height() - 20,
                    Qt.KeepAspectRatio, 
                    Qt.SmoothTransformation
                )
                main_window.original_img.setPixmap(pixmap_scaled)
        except:
            pass

    # Connect tab change event to refresh display
    if hasattr(main_window, 'tab_widget'):
        main_window.tab_widget.currentChanged.connect(lambda: refresh_register_tab_display(main_window))
    
    # Refresh display after short delay to ensure everything is loaded
    QTimer.singleShot(100, lambda: refresh_register_tab_display(main_window))
    
    # Thêm content widget vào scroll area và scroll area vào main layout
    scroll_area.setWidget(content_widget)
    main_layout.addWidget(scroll_area)
    
    # Apply animations
    setup_animation(owner_group, "fade")
    setup_animation(vehicle_group, "fade")


def setup_recognition_section(main_window, parent_layout):
    """Thiết lập phần nhận diện biển số với cấu trúc tối ưu"""
    recognition_group = QGroupBox("Nhận diện biển số")
    recognition_group.setFont(QFont("Arial", 12, QFont.Bold))
    
    # Layout chính
    main_layout = QVBoxLayout(recognition_group)
    
    # Grid Layout cho phần nhận diện - giúp kiểm soát vị trí chính xác
    grid_layout = QGridLayout()
    grid_layout.setVerticalSpacing(10)
    grid_layout.setHorizontalSpacing(20)
    
    # --- PHẦN TIÊU ĐỀ ---
    original_title = QLabel("Ảnh biển số:")
    original_title.setFont(QFont("Arial", 11, QFont.Bold))
    grid_layout.addWidget(original_title, 0, 0)
    
    result_title = QLabel("Kết quả nhận diện:")
    result_title.setFont(QFont("Arial", 11, QFont.Bold))
    grid_layout.addWidget(result_title, 0, 1)
    
    # --- PHẦN KHUNG ẢNH ---
    # Khung ảnh gốc
    if not hasattr(main_window, 'original_img'):
        main_window.original_img = QLabel()
        main_window.original_img.setAlignment(Qt.AlignCenter)
        main_window.original_img.setText("Chưa có ảnh")
        main_window.original_img.setStyleSheet(f"""
            background-color: {MyColor.BACKGROUND};
            border: 1px solid {MyColor.GRAY};
            border-radius: 5px;
        """)
    
    main_window.original_img.setFixedSize(400, 300)
    grid_layout.addWidget(main_window.original_img, 1, 0, Qt.AlignCenter)
    
    # Khung ảnh kết quả
    if not hasattr(main_window, 'processed_img'):
        main_window.processed_img = QLabel()
        main_window.processed_img.setAlignment(Qt.AlignCenter)
        main_window.processed_img.setText("Chưa có kết quả")
        main_window.processed_img.setStyleSheet(f"""
            background-color: {MyColor.BACKGROUND};
            border: 1px solid {MyColor.GRAY};
            border-radius: 5px;
        """)
    
    main_window.processed_img.setFixedSize(400, 300)
    grid_layout.addWidget(main_window.processed_img, 1, 1, Qt.AlignCenter)
    
    # --- PHẦN CÁC NÚT ĐIỀU KHIỂN ---
    # Container cho các nút - hàng thứ 2 trong grid
    upload_btn = create_styled_button("Tải ảnh lên", "upload", "secondary")
    upload_btn.setMinimumWidth(150)
    upload_btn.clicked.connect(lambda: upload_image(main_window))
    grid_layout.addWidget(upload_btn, 2, 0, Qt.AlignCenter)
    
    detect_btn = create_styled_button("Nhận diện biển số", "detect", "primary")
    detect_btn.setMinimumWidth(150)
    detect_btn.clicked.connect(lambda: detect_license_plate(main_window))
    grid_layout.addWidget(detect_btn, 2, 1, Qt.AlignCenter)
    
    # --- PHẦN KẾT QUẢ NHẬN DIỆN ---
    if not hasattr(main_window, 'recognition_result'):
        main_window.recognition_result = QLabel("Biển số nhận diện: ")
        main_window.recognition_result.setFont(QFont("Arial", 12, QFont.Bold))
        main_window.recognition_result.setStyleSheet(f"""
            color: {MyColor.PRIMARY}; 
            background-color: {MyColor.WHITE}; 
            padding: 10px; 
            border-radius: 5px;
            border: 1px solid {MyColor.LIGHT_GRAY};
        """)
        main_window.recognition_result.setAlignment(Qt.AlignCenter)
    
    # Kết quả nhận diện sẽ ở hàng thứ 3, chiếm 2 cột
    grid_layout.addWidget(main_window.recognition_result, 3, 0, 1, 2, Qt.AlignCenter)
    
    # Thêm grid layout vào layout chính
    main_layout.addLayout(grid_layout)
    
    # Thêm vào parent layout
    parent_layout.addWidget(recognition_group)
    
    # Thêm animation
    setup_animation(recognition_group, "slide_up")
    
    return recognition_group


def refresh_register_tab_display(main_window):
    """Refresh the registration tab display when switching tabs"""
    if hasattr(main_window, 'tab_widget') and main_window.tab_widget.currentIndex() == 0: 
        if hasattr(main_window, 'original_img'):
            main_window.original_img.setVisible(True)
            main_window.original_img.repaint()
        if hasattr(main_window, 'processed_img'):
            main_window.processed_img.setVisible(True)
            main_window.processed_img.repaint()
        if hasattr(main_window, 'recognition_result'):
            main_window.recognition_result.setVisible(True)
            main_window.recognition_result.repaint()
        main_window.repaint()


def upload_image(main_window):
    """Upload an image file for license plate recognition with improved performance"""
    try:
        file_name, _ = QFileDialog.getOpenFileName(
            main_window, 
            "Chọn ảnh biển số", 
            "", 
            "Image Files (*.png *.jpg *.jpeg *.bmp)"
        )
        
        if file_name:
            pixmap = QPixmap(file_name)
            if not pixmap.isNull():
                # Create loading effect
                main_window.original_img.setText("Đang tải ảnh...")
                main_window.recognition_result.setText("Đang xử lý...")
                
                # Sử dụng QThread để nhận diện biển số không block UI
                from PyQt5.QtCore import QThread, pyqtSignal
                
                class RecognitionWorker(QThread):
                    resultReady = pyqtSignal(str, object)
                    
                    def __init__(self, image_path):
                        super().__init__()
                        self.image_path = image_path
                        
                    def run(self):
                        try:
                            from utils.plate_recognition import recognize_license_plate, process_license_plate_image
                            plate_number = recognize_license_plate(self.image_path)
                            processed_img = process_license_plate_image(self.image_path)
                            
                            self.resultReady.emit(plate_number, processed_img)
                        except Exception as e:
                            logging.error(f"Error in recognition worker: {str(e)}")
                            self.resultReady.emit(None, None)
                
                # Hiển thị ảnh với kích thước phù hợp, giữ nguyên tỷ lệ
                pixmap_scaled = pixmap.scaled(
                    main_window.original_img.width() - 20,  # Trừ padding
                    main_window.original_img.height() - 20, # Trừ padding
                    Qt.KeepAspectRatio, 
                    Qt.SmoothTransformation
                )
                main_window.original_img.setPixmap(pixmap_scaled)
                main_window.original_img_path = file_name
                
                # Khởi tạo và chạy worker thread
                recognition_thread = RecognitionWorker(file_name)
                
                # Kết nối tín hiệu
                def handle_recognition_result(plate_number, processed_img):
                    try:
                        # Xử lý kết quả nhận dạng biển số
                        if plate_number:
                            main_window.plate_input.setText(plate_number)
                            main_window.recognition_result.setText(f"Biển số nhận diện: {plate_number}")
                            
                            # Nếu có kết quả thì tra mã tỉnh
                            if len(plate_number) >= 2 and plate_number[:2].isdigit():
                                # Dictionary mã tỉnh (đã có trong file license_plate_recognizer.py)
                                province_codes = {
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
                                
                                province_name = province_codes.get(plate_number[:2], "")
                                
                                # Cập nhật trường tỉnh/thành phố nếu tìm thấy
                                if province_name and hasattr(main_window, 'province_input'):
                                    index = main_window.province_input.findText(province_name, Qt.MatchContains)
                                    if index >= 0:
                                        main_window.province_input.setCurrentIndex(index)
                                    else:
                                        # Nếu không tìm thấy trong danh sách, ghi vào notes
                                        if hasattr(main_window, 'notes_input'):
                                            main_window.notes_input.setText(f"Tỉnh: {province_name}")
                            
                            # Hiển thị thông báo thành công
                            QMessageBox.information(
                                main_window,
                                "Nhận diện thành công",
                                f"Đã nhận diện biển số: {plate_number}",
                                QMessageBox.Ok
                            )
                        else:
                            main_window.recognition_result.setText("Biển số nhận diện: không nhận diện được")
                        
                        # Hiển thị ảnh đã xử lý (nếu có)
                        if processed_img is not None:
                            h, w, ch = processed_img.shape
                            bytes_per_line = ch * w
                            convert = QImage(processed_img.data, w, h, bytes_per_line, QImage.Format_RGB888)
                            pixmap = QPixmap.fromImage(convert)
                            
                            pixmap_scaled = pixmap.scaled(
                                main_window.processed_img.width() - 20,
                                main_window.processed_img.height() - 20,
                                Qt.KeepAspectRatio,
                                Qt.SmoothTransformation
                            )
                            main_window.processed_img.setPixmap(pixmap_scaled)
                            
                            # Hiệu ứng animation cho kết quả thành công
                            setup_animation(main_window.processed_img, "zoom_in")
                            setup_animation(main_window.recognition_result, "slide_right")
                        else:
                            main_window.processed_img.setText("Không thể xử lý ảnh")
                    except Exception as e:
                        logging.error(f"Error handling recognition result: {str(e)}")
                        main_window.recognition_result.setText("Lỗi xử lý kết quả nhận diện")
                
                recognition_thread.resultReady.connect(handle_recognition_result)
                recognition_thread.start()
                
                # Lưu trữ thread vào main_window để tránh bị garbage collected
                main_window._recognition_thread = recognition_thread
                
            else:
                QMessageBox.warning(main_window, "Lỗi", "Không thể tải ảnh, vui lòng thử lại.")
    except Exception as e:
        logging.error(f"Error in upload_image: {str(e)}")
        QMessageBox.critical(main_window, "Lỗi", f"Có lỗi xảy ra khi tải ảnh: {str(e)}")
def detect_license_plate(main_window):
    """Process image to detect and recognize license plate with improved performance"""
    try:
        if hasattr(main_window, 'original_img_path'):
            # Display loading message
            main_window.processed_img.setText("Đang xử lý ảnh...")
            main_window.recognition_result.setText("Đang nhận diện...")
            main_window.processed_img.repaint()
            main_window.recognition_result.repaint()
            
            # Sử dụng QThread để tránh block UI
            from PyQt5.QtCore import QThread, pyqtSignal
            
            class DetectionWorker(QThread):
                resultReady = pyqtSignal(str, object)
                
                def __init__(self, image_path):
                    super().__init__()
                    self.image_path = image_path
                    
                def run(self):
                    try:
                        from utils.plate_recognition import recognize_license_plate, process_license_plate_image
                        plate_number = recognize_license_plate(self.image_path)
                        processed_img = process_license_plate_image(self.image_path)
                        
                        self.resultReady.emit(plate_number, processed_img)
                    except Exception as e:
                        logging.error(f"Error in detection worker: {str(e)}")
                        self.resultReady.emit(None, None)
            
            # Khởi tạo worker thread
            detection_thread = DetectionWorker(main_window.original_img_path)
            
            # Xử lý kết quả
            def handle_detection_result(plate_number, processed_img):
                try:
                    # Hiển thị biển số nhận dạng được
                    if plate_number:
                        main_window.recognition_result.setText(f"Biển số nhận diện: {plate_number}")
                        
                        # Cập nhật trường biển số nếu chưa được điền
                        if not main_window.plate_input.text():
                            main_window.plate_input.setText(plate_number)
                            
                            # Kiểm tra và cập nhật tỉnh thành từ mã biển số
                            if len(plate_number) >= 2 and plate_number[:2].isdigit():
                                # Dictionary mã tỉnh
                                province_codes = {
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
                                
                                province_name = province_codes.get(plate_number[:2], "")
                                
                                # Cập nhật trường tỉnh/thành phố nếu tìm thấy
                                if province_name and hasattr(main_window, 'province_input'):
                                    index = main_window.province_input.findText(province_name, Qt.MatchContains)
                                    if index >= 0:
                                        main_window.province_input.setCurrentIndex(index)
                                    else:
                                        # Nếu không tìm thấy trong danh sách, ghi vào notes
                                        if hasattr(main_window, 'notes_input'):
                                            current_notes = main_window.notes_input.text()
                                            if not current_notes:
                                                main_window.notes_input.setText(f"Tỉnh: {province_name}")
                    else:
                        main_window.recognition_result.setText("Biển số nhận diện: không thành công")
                    
                    # Hiển thị ảnh đã xử lý
                    if processed_img is not None:
                        h, w, ch = processed_img.shape
                        bytes_per_line = ch * w
                        convert = QImage(processed_img.data, w, h, bytes_per_line, QImage.Format_RGB888)
                        pixmap = QPixmap.fromImage(convert)
                        
                        pixmap_scaled = pixmap.scaled(
                            main_window.processed_img.width() - 20,
                            main_window.processed_img.height() - 20,
                            Qt.KeepAspectRatio,
                            Qt.SmoothTransformation
                        )
                        main_window.processed_img.setPixmap(pixmap_scaled)
                        
                        # Hiệu ứng animation cho kết quả thành công
                        setup_animation(main_window.processed_img, "zoom_in")
                        setup_animation(main_window.recognition_result, "slide_right")
                    else:
                        main_window.processed_img.setText("Không thể xử lý ảnh")
                        
                except Exception as e:
                    logging.error(f"Error handling detection result: {str(e)}")
                    main_window.processed_img.setText("Lỗi xử lý ảnh")
                    main_window.recognition_result.setText("Lỗi xử lý kết quả nhận diện")
            
            # Kết nối tín hiệu và bắt đầu thread
            detection_thread.resultReady.connect(handle_detection_result)
            detection_thread.start()
            
            # Lưu trữ thread vào main_window để tránh bị garbage collected
            main_window._detection_thread = detection_thread
            
        else:
            QMessageBox.warning(
                main_window, 
                "Thông báo", 
                "Vui lòng tải ảnh lên trước khi thực hiện nhận diện."
            )
    except Exception as e:
        logging.error(f"Error in detect_license_plate: {str(e)}")
        QMessageBox.critical(main_window, "Lỗi", f"Có lỗi xảy ra khi nhận diện biển số: {str(e)}")
def register_vehicle(main_window):
    """Register a new vehicle with the entered information"""
    try:
        # Get form values
        owner_name = main_window.owner_name_input.text().strip()
        owner_phone = main_window.owner_phone_input.text().strip()
        plate_number = main_window.plate_input.text().strip()
        vehicle_type = main_window.vehicle_type_input.currentText()
        brand = main_window.brand_input.currentText()
        color = main_window.color_input.currentText()
        province = main_window.province_input.currentText()
        notes = main_window.notes_input.text().strip() if hasattr(main_window, 'notes_input') else ""
        
        # Validate required fields
        if not (owner_name and owner_phone and plate_number):
            QMessageBox.warning(
                main_window, 
                "Thông báo", 
                "Vui lòng điền đầy đủ thông tin bắt buộc (Chủ xe, Số điện thoại, Biển số)!"
            )
            return
        
        # Simple phone number validation
        if not owner_phone.isdigit() or len(owner_phone) < 9 or len(owner_phone) > 12:
            QMessageBox.warning(
                main_window, 
                "Lỗi", 
                "Số điện thoại không hợp lệ. Vui lòng chỉ nhập số và đảm bảo đúng định dạng!"
            )
            return
        
        # Create new vehicle entry using database
        try:
            db = DatabaseManager()
            success, result = db.add_vehicle(
                plate=plate_number,
                owner=owner_name,
                phone=owner_phone,
                vehicle_type=vehicle_type,
                brand=brand,
                color=color,
                province=province,
                notes=notes
            )
            
            if not success:
                QMessageBox.critical(
                    main_window, 
                    "Lỗi", 
                    f"Không thể đăng ký xe: {result}"
                )
                return
                
            # Lưu ảnh biển số nếu có
            if hasattr(main_window, 'original_img_path'):
                db.add_plate_image(plate_number, main_window.original_img_path)
            
            # Làm mới danh sách xe ở list tab
            from ui.list_tab import refresh_vehicle_list
            refresh_vehicle_list(main_window)
            
            # Clear form for next entry
            clear_register_form(main_window)
            
            # Show success message
            msg = QMessageBox(main_window)
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("Thành công")
            msg.setText(f"Đăng ký xe mới thành công!")
            msg.setInformativeText(f"Biển số: {plate_number}\nChủ xe: {owner_name}")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.setStyleSheet(f"QLabel{{min-width: 300px; color: {MyColor.PRIMARY};}}")
            
            # Add option to go to list tab
            view_list_btn = msg.addButton("Xem danh sách", QMessageBox.ActionRole)
            
            result = msg.exec_()
            
            # Switch to list tab if requested
            if msg.clickedButton() == view_list_btn and hasattr(main_window, 'tab_widget'):
                main_window.tab_widget.setCurrentIndex(1)  # Switch to list tab
                
        except Exception as e:
            QMessageBox.critical(
                main_window, 
                "Lỗi", 
                f"Không thể đăng ký xe: {str(e)}"
            )
    except Exception as e:
        logging.error(f"Error in register_vehicle: {str(e)}")
        QMessageBox.critical(main_window, "Lỗi", f"Có lỗi xảy ra khi đăng ký xe: {str(e)}")


def clear_register_form(main_window):
    """Clear the registration form for a new entry"""
    # Clear text inputs
    main_window.owner_name_input.clear()
    main_window.owner_phone_input.clear()
    main_window.plate_input.clear()
    
    # Reset combo boxes
    main_window.vehicle_type_input.setCurrentIndex(0)
    main_window.brand_input.setCurrentIndex(0)
    main_window.color_input.setCurrentIndex(0)
    
    # Clear notes if exists
    if hasattr(main_window, 'notes_input'):
        main_window.notes_input.clear()
    
    # Reset images
    main_window.original_img.setText("Chưa có ảnh")
    main_window.original_img.setPixmap(QPixmap())
    
    main_window.processed_img.setText("Chưa có kết quả")
    main_window.processed_img.setPixmap(QPixmap())
    
    main_window.recognition_result.setText("Biển số nhận diện: ")
    
    # Ensure widgets are visible
    main_window.original_img.setVisible(True)
    main_window.processed_img.setVisible(True)
    main_window.recognition_result.setVisible(True)
    
    # Clear stored image path
    if hasattr(main_window, 'original_img_path'):
        delattr(main_window, 'original_img_path')