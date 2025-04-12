from PyQt5.QtWidgets import (
    QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QGroupBox, QGridLayout, QMessageBox, QGraphicsOpacityEffect,
    QFrame, QSplitter, QWidget, QFileDialog
)
from PyQt5.QtGui import QPixmap, QFont, QColor, QBrush, QPainter, QPen
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer, QSize

from colors.my_colors import MyColor
from ui.style import setup_animation, create_title_label, create_styled_button
from utils.app_icons import AppIcons
from database.db_manager import DatabaseManager

def setup_search_tab(tab, window):
    """Set up the search tab with search controls and result display"""
    layout = QVBoxLayout(tab)
    layout.setSpacing(20)
    
    # Title with icon using helper function
    title_widget = create_title_label("TRA CỨU BIỂN SỐ XE", "search")
    layout.addWidget(title_widget)
    
    # Search group with improved controls
    search_group = QGroupBox("Nhập thông tin tra cứu")
    search_group.setFont(QFont("Arial", 12, QFont.Bold))
    search_layout = QVBoxLayout()
    
    # Search input with improved layout
    input_layout = QHBoxLayout()
    
    window.search_input = QLineEdit()
    window.search_input.setPlaceholderText("Nhập biển số xe cần tra cứu...")
    window.search_input.setMinimumHeight(40)
    
    # Add icon to search input
    window.search_input.addAction(AppIcons.get_icon("car"), QLineEdit.LeadingPosition)
    
    # Search button with icon
    search_button = create_styled_button("Tra cứu", "search", "secondary")
    search_button.setObjectName("searchButton")
    
    # Layout for search controls
    input_layout.addWidget(window.search_input, 3)
    input_layout.addWidget(search_button, 1)
    
    search_layout.addLayout(input_layout)
    
    # Additional search options (license plate scanner)
    scan_layout = QHBoxLayout()
    scan_label = QLabel("Hoặc sử dụng:")
    
    scan_button = create_styled_button("Quét ảnh biển số", "camera", "info")
    scan_layout.addWidget(scan_label)
    scan_layout.addWidget(scan_button)
    scan_layout.addStretch()
    
    search_layout.addLayout(scan_layout)
    search_group.setLayout(search_layout)
    layout.addWidget(search_group)
    setup_animation(search_group, "slide_right")
    
    # Results area with improved layout
    results_area = QSplitter(Qt.Horizontal)
    results_area.setHandleWidth(10)
    
    # Left side - vehicle information
    left_widget = QWidget()
    left_layout = QVBoxLayout(left_widget)
    
    # Vehicle information group
    result_group = QGroupBox("Thông tin xe")
    result_group.setFont(QFont("Arial", 12, QFont.Bold))
    result_layout = QGridLayout()
    
    window.owner_label = QLabel("Chủ xe:")
    window.owner_label.setFont(QFont("Arial", 10, QFont.Bold))
    window.owner_value = QLabel("-")
    window.owner_value.setStyleSheet(f"""
        color: {MyColor.TEXT_PRIMARY}; 
        background-color: {MyColor.BACKGROUND}; 
        padding: 10px; 
        border-radius: 4px;
        border: 1px solid {MyColor.LIGHT_GRAY};
    """)
    
    window.type_label = QLabel("Loại xe:")
    window.type_label.setFont(QFont("Arial", 10, QFont.Bold))
    window.type_value = QLabel("-")
    window.type_value.setStyleSheet(f"""
        color: {MyColor.TEXT_PRIMARY}; 
        background-color: {MyColor.BACKGROUND}; 
        padding: 10px; 
        border-radius: 4px;
        border: 1px solid {MyColor.LIGHT_GRAY};
    """)
    
    window.brand_label = QLabel("Hãng xe:")
    window.brand_label.setFont(QFont("Arial", 10, QFont.Bold))
    window.brand_value = QLabel("-")
    window.brand_value.setStyleSheet(f"""
        color: {MyColor.TEXT_PRIMARY}; 
        background-color: {MyColor.BACKGROUND}; 
        padding: 10px; 
        border-radius: 4px;
        border: 1px solid {MyColor.LIGHT_GRAY};
    """)
    
    window.phone_label = QLabel("Số điện thoại:")
    window.phone_label.setFont(QFont("Arial", 10, QFont.Bold))
    window.phone_value = QLabel("-")
    window.phone_value.setStyleSheet(f"""
        color: {MyColor.TEXT_PRIMARY}; 
        background-color: {MyColor.BACKGROUND}; 
        padding: 10px; 
        border-radius: 4px;
        border: 1px solid {MyColor.LIGHT_GRAY};
    """)
    
    window.time_label = QLabel("Thời gian đăng ký:")
    window.time_label.setFont(QFont("Arial", 10, QFont.Bold))
    window.time_value = QLabel("-")
    window.time_value.setStyleSheet(f"""
        color: {MyColor.TEXT_PRIMARY}; 
        background-color: {MyColor.BACKGROUND}; 
        padding: 10px; 
        border-radius: 4px;
        border: 1px solid {MyColor.LIGHT_GRAY};
    """)
    
    # Thêm trường notes (mới)
    window.notes_label = QLabel("Ghi chú:")
    window.notes_label.setFont(QFont("Arial", 10, QFont.Bold))
    window.notes_value = QLabel("-")
    window.notes_value.setStyleSheet(f"""
        color: {MyColor.TEXT_PRIMARY}; 
        background-color: {MyColor.BACKGROUND}; 
        padding: 10px; 
        border-radius: 4px;
        border: 1px solid {MyColor.LIGHT_GRAY};
    """)
    
    # Layout grid for vehicle information
    result_layout.addWidget(window.owner_label, 0, 0)
    result_layout.addWidget(window.owner_value, 0, 1)
    result_layout.addWidget(window.type_label, 1, 0)
    result_layout.addWidget(window.type_value, 1, 1)
    result_layout.addWidget(window.brand_label, 2, 0)
    result_layout.addWidget(window.brand_value, 2, 1)
    result_layout.addWidget(window.phone_label, 3, 0)
    result_layout.addWidget(window.phone_value, 3, 1)
    result_layout.addWidget(window.time_label, 4, 0)
    result_layout.addWidget(window.time_value, 4, 1)
    result_layout.addWidget(window.notes_label, 5, 0)
    result_layout.addWidget(window.notes_value, 5, 1)
    
    result_group.setLayout(result_layout)
    left_layout.addWidget(result_group)
    
    # Right side - license plate image and additional info
    right_widget = QWidget()
    right_layout = QVBoxLayout(right_widget)
    
    # Image group
    image_group = QGroupBox("Ảnh biển số")
    image_group.setFont(QFont("Arial", 12, QFont.Bold))
    image_layout = QVBoxLayout()
    
    # Improve image display
    window.image_label = QLabel()
    window.image_label.setFixedSize(320, 220)
    window.image_label.setAlignment(Qt.AlignCenter)
    window.image_label.setFrameShape(QFrame.StyledPanel)
    window.image_label.setStyleSheet(f"""
        border: 1px solid {MyColor.GRAY}; 
        background-color: {MyColor.BACKGROUND}; 
        border-radius: 8px;
        padding: 5px;
    """)
    window.image_label.setText("Chưa có ảnh")
    
    image_layout.addWidget(window.image_label, 0, Qt.AlignCenter)
    
    # Vehicle color preview
    color_layout = QHBoxLayout()
    color_label = QLabel("Màu xe:")
    color_label.setFont(QFont("Arial", 10, QFont.Bold))
    
    window.color_preview = QLabel()
    window.color_preview.setFixedSize(100, 30)
    window.color_preview.setFrameShape(QFrame.StyledPanel)
    window.color_preview.setStyleSheet(f"""
        background-color: {MyColor.WHITE}; 
        border: 1px solid {MyColor.GRAY};
        border-radius: 4px;
    """)
    
    color_layout.addWidget(color_label)
    color_layout.addWidget(window.color_preview)
    color_layout.addStretch()
    
    image_layout.addLayout(color_layout)
    image_group.setLayout(image_layout)
    right_layout.addWidget(image_group)
    
    # Add widgets to splitter
    results_area.addWidget(left_widget)
    results_area.addWidget(right_widget)
    results_area.setSizes([600, 400])
    
    # Add results area to main layout
    layout.addWidget(results_area)
    setup_animation(results_area, "fade")
    
    # Add bottom action buttons
    button_layout = QHBoxLayout()
    
    # Clear results button
    clear_btn = create_styled_button("Xóa kết quả", "refresh", "info") 
    clear_btn.setObjectName("clearButton")
    
    # Export info button
    export_btn = create_styled_button("Xuất thông tin", "export", "success")
    export_btn.setObjectName("exportInfoButton")
    
    # Print info button - new feature
    print_btn = create_styled_button("In thông tin", "print", "primary")
    
    # Add buttons to layout
    button_layout.addWidget(clear_btn)
    button_layout.addWidget(export_btn)
    button_layout.addWidget(print_btn)
    layout.addLayout(button_layout)
    
    # Connect event handlers
    def search_vehicle():
        """Search for a vehicle by license plate"""
        plate = window.search_input.text().strip()
        if not plate:
            QMessageBox.warning(tab, "Lỗi", "Vui lòng nhập biển số xe.")
            return
            
        # Show searching animation
        for widget in [window.owner_value, window.type_value, window.brand_value, 
                      window.phone_value, window.time_value, window.notes_value]:
            effect = QGraphicsOpacityEffect(widget)
            widget.setGraphicsEffect(effect)
            
            animation = QPropertyAnimation(effect, b"opacity")
            animation.setDuration(300)
            animation.setStartValue(1.0)
            animation.setEndValue(0.3)
            animation.start()

        # Display "searching" in the status bar if available
        if hasattr(window, 'statusBar'):
            window.statusBar().showMessage(f"Đang tìm kiếm biển số: {plate}...")
            
        # Delay slightly to show animation
        QTimer.singleShot(500, lambda: display_result(plate))

    def display_result(plate):
        """Display vehicle information after search"""
        # Sử dụng database manager để tìm xe
        db = DatabaseManager()
        vehicle = db.get_vehicle_by_plate(plate)
        
        if vehicle:
            # Update details with found vehicle data
            window.owner_value.setText(vehicle["owner"])
            window.type_value.setText(vehicle["type"])
            window.brand_value.setText(vehicle.get("brand", "Không có thông tin"))
            window.phone_value.setText(vehicle["phone"])
            window.time_value.setText(vehicle["timestamp"])
            window.notes_value.setText(vehicle.get("notes", "") or "Không có ghi chú")
            
            # Simulate color preview if color is available
            if "color" in vehicle and vehicle["color"]:
                # Map color names to RGB values
                color_map = {
                    "Đen": "#000000",
                    "Trắng": "#FFFFFF",
                    "Đỏ": "#FF0000",
                    "Xanh dương": "#0000FF",
                    "Xanh lá": "#00FF00",
                    "Vàng": "#FFFF00",
                    "Bạc": "#C0C0C0",
                    "Xám": "#808080",
                    "Nâu": "#A52A2A",
                    "Cam": "#FFA500",
                    "Hồng": "#FFC0CB",
                    "Tím": "#800080"
                }
                
                color_value = color_map.get(vehicle["color"], "#CCCCCC")
                window.color_preview.setStyleSheet(f"""
                    background-color: {color_value}; 
                    border: 1px solid {MyColor.GRAY};
                    border-radius: 4px;
                """)
            else:
                window.color_preview.setStyleSheet(f"""
                    background-color: {MyColor.LIGHT_GRAY}; 
                    border: 1px solid {MyColor.GRAY};
                    border-radius: 4px;
                """)
            
            # Hiển thị ảnh biển số nếu có
            if "image_path" in vehicle and vehicle["image_path"]:
                try:
                    plate_image = QPixmap(vehicle["image_path"])
                    if not plate_image.isNull():
                        window.image_label.setPixmap(plate_image.scaled(
                            320, 180, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                    else:
                        # Nếu không tải được ảnh, tạo ảnh giả lập
                        plate_image = generate_license_plate_image(vehicle["plate"], 320, 180)
                        window.image_label.setPixmap(plate_image)
                except:
                    # Nếu lỗi, tạo ảnh giả lập
                    plate_image = generate_license_plate_image(vehicle["plate"], 320, 180)
                    window.image_label.setPixmap(plate_image)
            else:
                # Tạo ảnh giả lập nếu không có ảnh thật
                plate_image = generate_license_plate_image(vehicle["plate"], 320, 180)
                window.image_label.setPixmap(plate_image)
            
            # Animate image display
            effect = QGraphicsOpacityEffect(window.image_label)
            window.image_label.setGraphicsEffect(effect)
            
            animation = QPropertyAnimation(effect, b"opacity")
            animation.setDuration(500)
            animation.setStartValue(0.3)
            animation.setEndValue(1.0)
            animation.start()
            
            # Fade in all value widgets
            for widget in [window.owner_value, window.type_value, window.brand_value, 
                          window.phone_value, window.time_value, window.notes_value]:
                effect = widget.graphicsEffect()
                
                animation = QPropertyAnimation(effect, b"opacity")
                animation.setDuration(500)
                animation.setStartValue(0.3)
                animation.setEndValue(1.0)
                animation.start()
                
            # Update status bar if available
            if hasattr(window, 'statusBar'):
                window.statusBar().showMessage(f"Đã tìm thấy xe biển số: {plate} - Chủ xe: {vehicle['owner']}")
        else:
            # No results found
            reset_values()
            
            # Show not found message
            QMessageBox.information(
                tab, 
                "Không tìm thấy", 
                f"Không tìm thấy thông tin cho biển số: {plate}\n\nVui lòng kiểm tra lại biển số xe hoặc đảm bảo xe đã được đăng ký."
            )
            
            # Update status bar if available
            if hasattr(window, 'statusBar'):
                window.statusBar().showMessage(f"Không tìm thấy thông tin cho biển số: {plate}")

    def reset_values():
        """Reset all search results to default values"""
        window.owner_value.setText("-")
        window.type_value.setText("-")
        window.brand_value.setText("-")
        window.phone_value.setText("-")
        window.time_value.setText("-")
        window.notes_value.setText("-")
        window.image_label.setText("Chưa có ảnh")
        window.image_label.setPixmap(QPixmap())
        window.color_preview.setStyleSheet(f"""
            background-color: {MyColor.WHITE}; 
            border: 1px solid {MyColor.GRAY};
            border-radius: 4px;
        """)

    def clear_search():
        """Clear search input and results"""
        window.search_input.clear()
        reset_values()
        
        # Animate clearing search
        effect = QGraphicsOpacityEffect(window.search_input)
        window.search_input.setGraphicsEffect(effect)
        
        animation = QPropertyAnimation(effect, b"opacity")
        animation.setDuration(300)
        animation.setStartValue(0.3)
        animation.setEndValue(1.0)
        animation.start()
        
        # Focus on search input after clearing
        window.search_input.setFocus()
        
        # Update status bar if available
        if hasattr(window, 'statusBar'):
            window.statusBar().showMessage("Tìm kiếm đã được xóa")
    
    def scan_license_plate():
        """Open camera or file dialog to scan license plate"""
        # For now, just use file dialog. In a real app, this would use a camera
        file_name, _ = QFileDialog.getOpenFileName(
            window, 
            "Chọn ảnh biển số", 
            "", 
            "Image Files (*.png *.jpg *.jpeg *.bmp)"
        )
        
        if file_name:
            # Simulate scanning process
            window.statusBar().showMessage("Đang quét ảnh biển số...") if hasattr(window, 'statusBar') else None
            
            # Create a progress dialog to simulate processing
            from PyQt5.QtWidgets import QProgressDialog
            progress = QProgressDialog("Đang xử lý ảnh biển số...", "Hủy", 0, 100, window)
            progress.setWindowModality(Qt.WindowModal)
            progress.setWindowTitle("Quét biển số")
            
            for i in range(101):
                progress.setValue(i)
                if progress.wasCanceled():
                    break
                window.processEvents()  # Keep UI responsive
                import time
                time.sleep(0.02)  # Simulate processing time
            
            # After "processing", use plate_recognition to detect plate
            from utils.plate_recognition import recognize_license_plate
            
            try:
                plate_number = recognize_license_plate(file_name)
                if plate_number:
                    window.search_input.setText(plate_number)
                    # Automatically search with the detected plate
                    search_vehicle()
                else:
                    QMessageBox.warning(
                        window,
                        "Không nhận diện được",
                        "Không thể nhận diện biển số từ ảnh này. Vui lòng thử ảnh khác hoặc nhập biển số trực tiếp."
                    )
            except Exception as e:
                QMessageBox.warning(
                    window,
                    "Lỗi",
                    f"Không thể xử lý ảnh: {str(e)}"
                )
    
    def export_vehicle_info():
        """Export the current vehicle information to a PDF or text file"""
        # Check if there's any vehicle info to export
        if window.owner_value.text() == "-":
            QMessageBox.warning(tab, "Lỗi", "Không có thông tin xe để xuất!")
            return
            
        # Get export file name and type
        file_name, _ = QFileDialog.getSaveFileName(
            window, 
            "Xuất thông tin xe", 
            "", 
            "PDF Files (*.pdf);;Text Files (*.txt)"
        )
        
        if not file_name:
            return
            
        try:
            # Simple text file export for now
            if file_name.endswith('.txt'):
                with open(file_name, 'w', encoding='utf-8') as f:
                    f.write("THÔNG TIN XE\n")
                    f.write("="*50 + "\n\n")
                    f.write(f"Biển số: {window.search_input.text()}\n")
                    f.write(f"Chủ xe: {window.owner_value.text()}\n")
                    f.write(f"Loại xe: {window.type_value.text()}\n")
                    f.write(f"Hãng xe: {window.brand_value.text()}\n")
                    f.write(f"Màu xe: {window.color_preview.styleSheet().split('background-color:')[1].split(';')[0].strip()}\n")
                    f.write(f"Số điện thoại: {window.phone_value.text()}\n")
                    f.write(f"Thời gian đăng ký: {window.time_value.text()}\n")
                    f.write(f"Ghi chú: {window.notes_value.text()}\n")
                    
                QMessageBox.information(
                    tab, 
                    "Xuất thành công", 
                    f"Đã xuất thông tin xe ra file: {file_name}"
                )
            elif file_name.endswith('.pdf'):
                # Show a message that PDF export would be implemented in a real app
                QMessageBox.information(
                    tab, 
                    "Thông báo", 
                    "Tính năng xuất ra file PDF sẽ được phát triển trong phiên bản tiếp theo."
                )
        except Exception as e:
            QMessageBox.warning(tab, "Lỗi", f"Không thể xuất thông tin: {str(e)}")
    
    def print_vehicle_info():
        """Print the current vehicle information"""
        # Show a message that printing would be implemented in a real app
        QMessageBox.information(
            tab, 
            "Thông báo", 
            "Tính năng in thông tin sẽ được phát triển trong phiên bản tiếp theo."
        )
    
    # Function to be called when tab is activated
    def on_tab_activated():
        """Reset all values when switching to this tab"""
        reset_values()
        
        # Apply a fresh animation to result group for better visual feedback
        for group in [result_group, image_group]:
            effect = QGraphicsOpacityEffect(group)
            group.setGraphicsEffect(effect)
            
            animation = QPropertyAnimation(effect, b"opacity")
            animation.setDuration(400)
            animation.setStartValue(0.5)
            animation.setEndValue(1.0)
            animation.start()
        
        # Focus on search input for immediate use
        window.search_input.setFocus()
    
    # Store the reset function for access from main_window.py
    window.reset_search_tab = on_tab_activated

    # Connect signals to slots
    search_button.clicked.connect(search_vehicle)
    clear_btn.clicked.connect(clear_search)
    window.search_input.returnPressed.connect(search_vehicle)
    scan_button.clicked.connect(scan_license_plate)
    export_btn.clicked.connect(export_vehicle_info)
    print_btn.clicked.connect(print_vehicle_info)


def generate_license_plate_image(plate_text, width, height):
    """Generate a simple rendered license plate image with the given text"""
    pixmap = QPixmap(width, height)
    pixmap.fill(QColor(255, 255, 255))  # White background
    
    painter = QPainter(pixmap)
    
    # Draw license plate background
    painter.setBrush(QBrush(QColor("#f0f0f0")))  # Light gray background
    painter.setPen(QPen(QColor("#000000"), 2))  # Black border
    
    # Draw rounded rectangle for plate
    painter.drawRoundedRect(10, 10, width - 20, height - 20, 10, 10)
    
    # Draw blue bar on top (like Vietnamese license plates)
    painter.setBrush(QBrush(QColor("#003399")))  # Blue
    painter.setPen(Qt.NoPen)
    painter.drawRect(15, 15, width - 30, 30)
    
    # Draw "VIỆT NAM" text in the blue bar
    painter.setPen(QPen(QColor("#ffffff")))  # White text
    painter.setFont(QFont("Arial", 12, QFont.Bold))
    painter.drawText(width // 2 - 40, 35, "VIỆT NAM")
    
    # Draw license plate number
    painter.setPen(QPen(QColor("#000000")))  # Black text
    painter.setFont(QFont("Arial", 30, QFont.Bold))
    painter.drawText(width // 2 - painter.fontMetrics().width(plate_text) // 2, height // 2 + 20, plate_text)
    
    # Draw some decorative elements
    painter.setPen(QPen(QColor("#444444"), 1))
    painter.drawLine(15, height - 40, width - 15, height - 40)
    
    # Add some security-like patterns
    painter.setPen(QPen(QColor("#bbbbbb"), 1, Qt.DashLine))
    for i in range(5):
        painter.drawLine(20 + i * 30, height - 30, 40 + i * 30, height - 20)
    
    painter.end()
    
    return pixmap