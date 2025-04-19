from PyQt5.QtWidgets import (
    QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QGroupBox, QGridLayout, QMessageBox, QGraphicsOpacityEffect,
    QFrame, QSplitter, QWidget, QFileDialog, QDialog, QFormLayout,
    QProgressDialog, QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QInputDialog
)
from PyQt5.QtGui import QPixmap, QFont, QColor, QBrush, QPainter, QPen
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer, QSize, QDate

from colors.my_colors import MyColor
from ui.style import setup_animation, create_title_label, create_styled_button
from utils.app_icons import AppIcons
from database.db_manager import DatabaseManager
import logging

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
    window.province_label = QLabel("Tỉnh/Thành phố:")
    window.province_label.setFont(QFont("Arial", 10, QFont.Bold))
    window.province_value = QLabel("-")
    window.province_value.setStyleSheet(f"""
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
    result_layout.addWidget(window.province_label, 3, 0)
    result_layout.addWidget(window.province_value, 3, 1)
    result_layout.addWidget(window.phone_label, 4, 0)
    result_layout.addWidget(window.phone_value, 4, 1)
    result_layout.addWidget(window.time_label, 5, 0)
    result_layout.addWidget(window.time_value, 5, 1)
    result_layout.addWidget(window.notes_label, 6, 0)
    result_layout.addWidget(window.notes_value, 6, 1)
    
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
    
    # Thêm nút Xem lịch sử mới
    history_btn = create_styled_button("Xem lịch sử", "history", "info")
    history_btn.setObjectName("historyButton")
    
    # Add buttons to layout
    button_layout.addWidget(clear_btn)
    button_layout.addWidget(export_btn)
    button_layout.addWidget(print_btn)
    button_layout.addWidget(history_btn) 
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
            # Tạo dialog hiển thị thông tin xe
            result_dialog = QDialog(window)
            result_dialog.setWindowTitle("Thông tin xe")
            result_dialog.setMinimumWidth(400)
            result_dialog.setWindowIcon(AppIcons.get_icon("car"))
            
            dialog_layout = QVBoxLayout(result_dialog)
            
            # Thông tin chủ xe
            owner_group = QGroupBox("Thông tin chủ xe")
            owner_layout = QFormLayout()
            
            owner_name = QLineEdit(vehicle.get("owner", ""))
            owner_name.setReadOnly(True)
            owner_name.setStyleSheet("background-color: #f8f8f8; border: 1px solid #ccc; border-radius: 4px; padding: 5px;")
            
            phone = QLineEdit(vehicle.get("phone", ""))
            phone.setReadOnly(True)
            phone.setStyleSheet("background-color: #f8f8f8; border: 1px solid #ccc; border-radius: 4px; padding: 5px;")
            
            owner_layout.addRow("Họ tên:", owner_name)
            owner_layout.addRow("Số điện thoại:", phone)
            owner_group.setLayout(owner_layout)
            
            # Thông tin xe
            vehicle_group = QGroupBox("Thông tin xe")
            vehicle_layout = QFormLayout()
            
            plate_number = QLineEdit(vehicle.get("plate", ""))
            plate_number.setReadOnly(True)
            plate_number.setStyleSheet("background-color: #f8f8f8; border: 1px solid #ccc; border-radius: 4px; padding: 5px; font-weight: bold;")
            
            vehicle_type = QLineEdit(vehicle.get("type", ""))
            vehicle_type.setReadOnly(True)
            vehicle_type.setStyleSheet("background-color: #f8f8f8; border: 1px solid #ccc; border-radius: 4px; padding: 5px;")
            
            brand = QLineEdit(vehicle.get("brand", ""))
            brand.setReadOnly(True)
            brand.setStyleSheet("background-color: #f8f8f8; border: 1px solid #ccc; border-radius: 4px; padding: 5px;")
            
            color = QLineEdit(vehicle.get("color", ""))
            color.setReadOnly(True)
            color.setStyleSheet("background-color: #f8f8f8; border: 1px solid #ccc; border-radius: 4px; padding: 5px;")
            province = QLineEdit(vehicle.get("province", ""))
            province.setReadOnly(True)
            province.setStyleSheet("background-color: #f8f8f8; border: 1px solid #ccc; border-radius: 4px; padding: 5px;")
            notes = QLineEdit(vehicle.get("notes", "") or "Không có ghi chú")
            notes.setReadOnly(True)
            notes.setStyleSheet("background-color: #f8f8f8; border: 1px solid #ccc; border-radius: 4px; padding: 5px;")
            
            vehicle_layout.addRow("Biển số xe:", plate_number)
            vehicle_layout.addRow("Loại xe:", vehicle_type)
            vehicle_layout.addRow("Hãng xe:", brand)
            vehicle_layout.addRow("Màu xe:", color)
            vehicle_layout.addRow("Tỉnh/Thành phố:", province)
            vehicle_layout.addRow("Ghi chú:", notes)
            vehicle_group.setLayout(vehicle_layout)
            
            # Thêm các group vào layout chính
            dialog_layout.addWidget(owner_group)
            dialog_layout.addWidget(vehicle_group)
            
            # Nút điều khiển
            button_layout = QHBoxLayout()
            
            # Tạo một phiên bản cục bộ của export_vehicle_info cho dialog này
            def export_dialog_vehicle_info():
                # Get export file name and type
                file_name, _ = QFileDialog.getSaveFileName(
                    result_dialog, 
                    "Xuất thông tin xe", 
                    "", 
                    "PDF Files (*.pdf);;Text Files (*.txt);;HTML Files (*.html)"
                )
                
                if not file_name:
                    return
                    
                try:
                    # Sử dụng thông tin từ các trường trong dialog
                    if file_name.endswith('.txt'):
                        with open(file_name, 'w', encoding='utf-8') as f:
                            f.write("THÔNG TIN XE\n")
                            f.write("="*50 + "\n\n")
                            f.write(f"Biển số: {plate_number.text()}\n")
                            f.write(f"Chủ xe: {owner_name.text()}\n")
                            f.write(f"Số điện thoại: {phone.text()}\n")
                            f.write(f"Loại xe: {vehicle_type.text()}\n")
                            f.write(f"Hãng xe: {brand.text()}\n")
                            f.write(f"Màu xe: {color.text()}\n")
                            f.write(f"Tỉnh/Thành phố: {province.text()}\n")
                            f.write(f"Thời gian đăng ký: {vehicle.get('timestamp', '')}\n")
                            f.write(f"Ghi chú: {notes.text()}\n")
                            
                        QMessageBox.information(
                            result_dialog, 
                            "Xuất thành công", 
                            f"Đã xuất thông tin xe ra file: {file_name}"
                        )
                    elif file_name.endswith('.html'):
                        # Xuất ra HTML với định dạng đẹp
                        html_content = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Thông tin xe {plate_number.text()}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            color: #333;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
            border: 1px solid #ddd;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2E5077;
            text-align: center;
            border-bottom: 2px solid #4DA1A9;
            padding-bottom: 10px;
        }}
        .info-group {{
            margin-bottom: 20px;
        }}
        .info-row {{
            display: flex;
            border-bottom: 1px solid #eee;
            padding: 10px 0;
        }}
        .info-label {{
            width: 180px;
            font-weight: bold;
            color: #2E5077;
        }}
        .info-value {{
            flex: 1;
        }}
        .plate-number {{
            text-align: center;
            font-size: 24px;
            font-weight: bold;
            margin: 20px 0;
            padding: 15px;
            background-color: #f5f5f5;
            border-radius: 8px;
        }}
        .footer {{
            text-align: center;
            margin-top: 30px;
            font-size: 12px;
            color: #777;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>THÔNG TIN XE</h1>
        
        <div class="plate-number">
            Biển số: {plate_number.text()}
        </div>
        
        <div class="info-group">
            <div class="info-row">
                <div class="info-label">Chủ xe:</div>
                <div class="info-value">{owner_name.text()}</div>
            </div>
            <div class="info-row">
                <div class="info-label">Số điện thoại:</div>
                <div class="info-value">{phone.text()}</div>
            </div>
            <div class="info-row">
                <div class="info-label">Loại xe:</div>
                <div class="info-value">{vehicle_type.text()}</div>
            </div>
            <div class="info-row">
                <div class="info-label">Hãng xe:</div>
                <div class="info-value">{brand.text()}</div>
            </div>
            <div class="info-row">
                <div class="info-label">Màu xe:</div>
                <div class="info-value">{color.text()}</div>
            </div>
            <div class="info-row">
                <div class="info-label">Tỉnh/Thành phố:</div>
                <div class="info-value">{province.text()}</div>
            </div>
            <div class="info-row">
                <div class="info-label">Thời gian đăng ký:</div>
                <div class="info-value">{vehicle.get('timestamp', '')}</div>
            </div>
            <div class="info-row">
                <div class="info-label">Ghi chú:</div>
                <div class="info-value">{notes.text()}</div>
            </div>
        </div>
        
        <div class="footer">
            Thông tin được xuất từ Hệ thống Quản lý Đăng ký Xe - {QDate.currentDate().toString("dd/MM/yyyy")}
        </div>
    </div>
</body>
</html>"""
                        
                        with open(file_name, 'w', encoding='utf-8') as f:
                            f.write(html_content)
                            
                        QMessageBox.information(
                            result_dialog, 
                            "Xuất thành công", 
                            f"Đã xuất thông tin xe ra file HTML: {file_name}"
                        )
                    elif file_name.endswith('.pdf'):
                        # Sử dụng VehicleExporter để xuất ra PDF
                        from database.vehicle_model import export_vehicle_info_to_pdf
                        
                        vehicle_info = {
                            "plate": plate_number.text(),
                            "owner": owner_name.text(),
                            "phone": phone.text(),
                            "type": vehicle_type.text(),
                            "brand": brand.text(),
                            "color": color.text(),
                            "province": province.text(),
                            "timestamp": vehicle.get('timestamp', ''),
                            "notes": notes.text()
                        }
                        
                        if export_vehicle_info_to_pdf(vehicle_info, file_name):
                            QMessageBox.information(
                                result_dialog, 
                                "Xuất thành công", 
                                f"Đã xuất thông tin xe ra file PDF: {file_name}"
                            )
                        else:
                            QMessageBox.warning(
                                result_dialog, 
                                "Lỗi", 
                                "Không thể xuất thông tin ra file PDF. Vui lòng kiểm tra lại cài đặt."
                            )
                except Exception as e:
                    logging.error(f"Error exporting vehicle info: {str(e)}")
                    QMessageBox.warning(result_dialog, "Lỗi", f"Không thể xuất thông tin: {str(e)}")
            
            export_btn = create_styled_button("Xuất thông tin", "export", "success")
            export_btn.clicked.connect(export_dialog_vehicle_info)
            
            close_btn = create_styled_button("Đóng", "cancel", "danger")
            close_btn.clicked.connect(result_dialog.reject)
            
            button_layout.addWidget(export_btn)
            button_layout.addWidget(close_btn)
            dialog_layout.addLayout(button_layout)
            
            # Hiển thị dialog
            result_dialog.exec_()
            
            # Update status bar if available
            if hasattr(window, 'statusBar'):
                window.statusBar().showMessage(f"Đã tìm thấy xe biển số: {plate} - Chủ xe: {vehicle['owner']}")
        else:
            # No results found
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
        window.province_value.setText("-")
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
        """Open file dialog to scan license plate image using the same algorithm as register_tab"""
        try:
            file_name, _ = QFileDialog.getOpenFileName(
                window, 
                "Chọn ảnh biển số", 
                "", 
                "Image Files (*.png *.jpg *.jpeg *.bmp)"
            )
            
            if file_name:
                # Display loading message in status bar if available
                if hasattr(window, 'statusBar'):
                    window.statusBar().showMessage("Đang xử lý ảnh biển số...")
                
                # Create loading effect with progress dialog
                progress = QProgressDialog("Đang xử lý ảnh biển số...", "Hủy", 0, 100, window)
                progress.setWindowModality(Qt.WindowModal)
                progress.setWindowTitle("Quét biển số")
                progress.setMinimumDuration(500)  # Only show if operation takes more than 500ms
                
                # Define function to process image with proper error handling
                def process_image():
                    try:
                        # Use the same plate recognition function as in register_tab.py
                        from utils.plate_recognition import recognize_license_plate
                        
                        # Try to recognize the plate number
                        plate_number = recognize_license_plate(file_name)
                        
                        # Update progress to 100%
                        progress.setValue(100)
                        
                        if plate_number:
                            # Set the recognized plate number in search input
                            window.search_input.setText(plate_number)
                            
                            # Show a notification
                            QMessageBox.information(
                                window,
                                "Nhận diện thành công",
                                f"Đã nhận diện biển số: {plate_number}",
                                QMessageBox.Ok
                            )
                            
                            # Automatically search with the detected plate
                            search_vehicle()
                        else:
                            QMessageBox.warning(
                                window,
                                "Không nhận diện được",
                                "Không thể nhận diện biển số từ ảnh này. Vui lòng thử ảnh khác hoặc nhập biển số trực tiếp."
                            )
                    except Exception as e:
                        logging.error(f"Error in license plate recognition: {str(e)}")
                        QMessageBox.critical(
                            window,
                            "Lỗi",
                            f"Có lỗi xảy ra khi nhận diện biển số: {str(e)}"
                        )
                    finally:
                        # Close progress dialog if it's still open
                        if progress.isVisible():
                            progress.close()
                        
                        # Reset status bar message
                        if hasattr(window, 'statusBar'):
                            window.statusBar().showMessage("Sẵn sàng", 3000)
                
                # Use timer to allow UI to update before processing starts
                QTimer.singleShot(100, process_image)
        except Exception as e:
            logging.error(f"Error in scan_license_plate: {str(e)}")
            QMessageBox.critical(window, "Lỗi", f"Có lỗi xảy ra: {str(e)}")
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

    # Hàm xử lý khi nhấn nút Xem lịch sử
    def view_history():
        """Hiển thị lịch sử thay đổi của xe đang xem"""
        if window.owner_value.text() == "-":
            QMessageBox.warning(tab, "Lỗi", "Không có thông tin xe để xem lịch sử.")
            return
            
        # Lấy biển số xe đang tìm
        plate = window.search_input.text().strip()
        if not plate:
            QMessageBox.warning(tab, "Lỗi", "Không có thông tin biển số.")
            return
            
        # Lấy thông tin xe
        db = DatabaseManager()
        vehicle = db.get_vehicle_by_plate(plate)
        
        if not vehicle:
            QMessageBox.warning(tab, "Lỗi", "Không thể tìm thấy thông tin xe này.")
            return
            
        # Lấy lịch sử thay đổi
        history_list = db.get_vehicle_history(vehicle.get("id"))
        
        if not history_list:
            QMessageBox.information(
                tab, 
                "Thông báo",
                f"Không có lịch sử thay đổi nào cho xe biển số {plate}."
            )
            return
        
        # Hiển thị dialog lịch sử
        show_history_dialog(window, plate, history_list)

    # Định nghĩa hàm hiển thị dialog lịch sử
    def show_history_dialog(main_window, plate, history_list):
        """Hiển thị dialog lịch sử thay đổi"""
        dialog = QDialog(main_window)
        dialog.setWindowTitle(f"Lịch sử thay đổi - Biển số: {plate}")
        dialog.setMinimumWidth(650)
        dialog.setMinimumHeight(400)
        
        layout = QVBoxLayout(dialog)
        
        # Tiêu đề
        title_label = QLabel(f"LỊCH SỬ THAY ĐỔI XE BIỂN SỐ: {plate}")
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Bảng lịch sử
        history_table = QTableWidget()
        history_table.setColumnCount(4)
        history_table.setHorizontalHeaderLabels([
            "STT", "Loại thay đổi", "Thời gian", "Mô tả"
        ])
        history_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        history_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        history_table.setAlternatingRowColors(True)
        
        # Thiết lập độ rộng cột
        header = history_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # STT
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Loại thay đổi
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Thời gian
        header.setSectionResizeMode(3, QHeaderView.Stretch)           # Mô tả
        
        # Thêm dữ liệu vào bảng
        history_table.setRowCount(len(history_list))
        
        for i, history in enumerate(history_list):
            # STT
            stt_item = QTableWidgetItem(str(i + 1))
            stt_item.setTextAlignment(Qt.AlignCenter)
            history_table.setItem(i, 0, stt_item)
            
            # Loại thay đổi - Chuyển đổi sang tiếng Việt
            change_type = history.get("change_type", "")
            change_type_text = {
                "ADD": "Thêm mới",
                "UPDATE": "Cập nhật",
                "DELETE": "Xóa"
            }.get(change_type, change_type)
            
            change_type_item = QTableWidgetItem(change_type_text)
            
            # Màu sắc theo loại thay đổi
            if change_type == "ADD":
                change_type_item.setForeground(QBrush(QColor(MyColor.SUCCESS)))
            elif change_type == "UPDATE":
                change_type_item.setForeground(QBrush(QColor(MyColor.INFO)))
            elif change_type == "DELETE":
                change_type_item.setForeground(QBrush(QColor(MyColor.DANGER)))
            
            change_type_item.setTextAlignment(Qt.AlignCenter)
            history_table.setItem(i, 1, change_type_item)
            
            # Thời gian
            time_item = QTableWidgetItem(history.get("change_time", ""))
            time_item.setTextAlignment(Qt.AlignCenter)
            history_table.setItem(i, 2, time_item)
            
            # Mô tả
            desc_item = QTableWidgetItem(history.get("description", ""))
            history_table.setItem(i, 3, desc_item)
        
        layout.addWidget(history_table)
        
        # Nút đóng
        close_btn = create_styled_button("Đóng", "cancel", "danger")
        close_btn.clicked.connect(dialog.reject)
        
        # Layout cho các nút
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)
        
        dialog.exec_()

    # Kết nối nút với hàm xử lý
    history_btn.clicked.connect(view_history)
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