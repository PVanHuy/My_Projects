from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit,
    QAbstractItemView, QGroupBox, QFileDialog, QMessageBox,
    QFormLayout, QDialog, QDateEdit, QCheckBox, QSpacerItem,
    QSizePolicy, QInputDialog
)
from PyQt5.QtGui import QFont, QIcon, QColor, QBrush
from PyQt5.QtCore import Qt, QSize, QDate

from colors.my_colors import MyColor
from ui.style import apply_stylesheet, setup_animation, create_title_label, create_styled_button
from utils.app_icons import AppIcons
from database.db_manager import DatabaseManager
import logging

# Cấu hình logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
def edit_selected_vehicle(main_window):
    """Edit the selected vehicle's information"""
    try:
        selected_row = main_window.vehicle_table.currentRow()
        if selected_row >= 0:
            # Get the plate number of the selected row
            plate = main_window.vehicle_table.item(selected_row, 1).text()
            
            # Fetch current vehicle data
            db = DatabaseManager()
            vehicle = db.get_vehicle_by_plate(plate)
            
            if not vehicle:
                QMessageBox.warning(
                    main_window,
                    "Lỗi",
                    "Không thể tìm thấy thông tin xe này."
                )
                return
            
            # Create edit dialog
            dialog = QDialog(main_window)
            dialog.setWindowTitle("Sửa thông tin xe")
            dialog.setMinimumWidth(400)
            
            layout = QVBoxLayout(dialog)
            
            # Owner info
            owner_group = QGroupBox("Thông tin chủ xe")
            owner_form = QFormLayout()
            
            owner_name_input = QLineEdit()
            owner_name_input.setText(vehicle.get("owner", ""))
            
            owner_phone_input = QLineEdit()
            owner_phone_input.setText(vehicle.get("phone", ""))
            
            owner_form.addRow("Họ tên:", owner_name_input)
            owner_form.addRow("Số điện thoại:", owner_phone_input)
            owner_group.setLayout(owner_form)
            
            # Vehicle info
            vehicle_group = QGroupBox("Thông tin xe")
            vehicle_form = QFormLayout()
            
            # Display plate number (read-only)
            plate_input = QLineEdit()
            plate_input.setText(vehicle.get("plate", ""))
            plate_input.setReadOnly(True)
            plate_input.setEnabled(False)
            
            vehicle_type_input = QComboBox()
            vehicle_type_input.addItems(["Xe ô tô", "Xe khách", "Xe máy", "Khác"])
            # Set current type
            index = vehicle_type_input.findText(vehicle.get("type", ""))
            if index >= 0:
                vehicle_type_input.setCurrentIndex(index)
            
            brand_input = QComboBox()
            brand_input.addItems(["Toyota", "Honda", "Mazda", "Ford", "Hyundai", 
            "Kia", "Mercedes-Benz", "BMW", "Audi", "Chevrolet",
            "Nissan", "Mitsubishi", "Suzuki", "Yamaha", "Khác"])
            brand_input.setEditable(True)
            # Set current brand
            brand_input.setCurrentText(vehicle.get("brand", ""))
            
            color_input = QLineEdit()
            color_input.setText(vehicle.get("color", ""))
            province_input = QComboBox()
            province_input.addItems([
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
            # Set current province
            province_input.setCurrentText(vehicle.get("province", "Hà Nội"))
            
            notes_input = QLineEdit()
            notes_input.setPlaceholderText("Ghi chú (không bắt buộc)")

            vehicle_form.addRow("Biển số xe:", plate_input)
            vehicle_form.addRow("Loại xe:", vehicle_type_input)
            vehicle_form.addRow("Hãng xe:", brand_input)
            vehicle_form.addRow("Màu xe:", color_input)
            vehicle_form.addRow("Tỉnh/Thành phố:", province_input)  # Thêm vào form
            vehicle_form.addRow("Ghi chú:", notes_input)
            vehicle_group.setLayout(vehicle_form)
            
            # Add to layout
            layout.addWidget(owner_group)
            layout.addWidget(vehicle_group)
            
            # Buttons
            buttons_layout = QHBoxLayout()
            
            save_btn = create_styled_button("Lưu thay đổi", "save", "success")
            cancel_btn = create_styled_button("Hủy", "cancel", "danger")
            
            buttons_layout.addWidget(save_btn)
            buttons_layout.addWidget(cancel_btn)
            layout.addLayout(buttons_layout)
            
            # Handle save
            def save_changes():
                # Validate
                if not (owner_name_input.text() and owner_phone_input.text()):
                    QMessageBox.warning(dialog, "Lỗi", "Vui lòng điền đầy đủ thông tin bắt buộc!")
                    return
                
                # Update vehicle info
                try:
                    updates = {
                        'owner': owner_name_input.text(),
                        'phone': owner_phone_input.text(),
                        'vehicle_type': vehicle_type_input.currentText(),
                        'brand': brand_input.currentText(),
                        'color': color_input.text(),
                        'province': province_input.currentText(),
                        'notes': notes_input.text()
                    }
                    
                    success, result = db.update_vehicle(plate, **updates)
                    
                    if success:
                        # Refresh the list
                        refresh_vehicle_list(main_window)
                        
                        QMessageBox.information(dialog, "Thành công", "Đã cập nhật thông tin xe thành công!")
                        dialog.accept()
                    else:
                        QMessageBox.critical(dialog, "Lỗi", f"Không thể cập nhật thông tin xe: {result}")
                    
                except Exception as e:
                    QMessageBox.critical(dialog, "Lỗi", f"Không thể cập nhật thông tin xe: {str(e)}")
            
            # Connect buttons
            save_btn.clicked.connect(save_changes)
            cancel_btn.clicked.connect(dialog.reject)
            
            dialog.exec_()
        else:
            QMessageBox.warning(
                main_window,
                "Lỗi",
                "Vui lòng chọn xe cần sửa trong danh sách."
            )
    except Exception as e:
        logging.error(f"Error in edit_selected_vehicle: {str(e)}")
        QMessageBox.critical(main_window, "Lỗi", f"Có lỗi xảy ra khi sửa thông tin xe: {str(e)}")
def setup_list_tab(tab, main_window):
    """Set up the list tab with table and controls"""
    layout = QVBoxLayout(tab)
    layout.setSpacing(20)

    # Add title with icon using helper function
    title_widget = create_title_label("DANH SÁCH XE ĐÃ ĐĂNG KÝ", "list")
    layout.addWidget(title_widget)

    # Filter group box with enhanced controls
    filter_group = QGroupBox("Tìm kiếm và lọc")
    filter_group.setFont(QFont("Arial", 12, QFont.Bold))
    filter_layout = QHBoxLayout()
    
    # Search input
    search_label = QLabel("Tìm kiếm:")
    search_input = QLineEdit()
    search_input.setPlaceholderText("Nhập biển số, chủ xe hoặc số điện thoại...")
    search_input.setMinimumWidth(250)
    
    # Vehicle type filter
    type_label = QLabel("Loại xe:")
    type_combo = QComboBox()
    type_combo.addItem("Tất cả")
    type_combo.addItems(["Xe ô tô", "Xe khách", "Xe máy", "Khác"])
    
    # Brand filter
    brand_label = QLabel("Hãng xe:")
    brand_combo = QComboBox()
    brand_combo.addItem("Tất cả")
    brand_combo.addItems(["Toyota", "Honda", "Mazda", "Ford", "Hyundai", 
            "Kia", "Mercedes-Benz", "BMW", "Audi", "Chevrolet",
            "Nissan", "Mitsubishi", "Suzuki", "Yamaha", "Khác"])
    # Province filter
    province_label = QLabel("Tỉnh/TP:")
    province_combo = QComboBox()
    province_combo.addItem("Tất cả")
    province_combo.addItems([
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
    # Date filter
    date_label = QLabel("Ngày đăng ký:")
    date_filter = QDateEdit()
    date_filter.setCalendarPopup(True)
    date_filter.setDate(QDate.currentDate())
    
    # Add checkbox to enable/disable date filter
    date_check = QCheckBox("Lọc theo ngày")
    date_check.setChecked(False)
    date_filter.setEnabled(False)
    
    # Connect checkbox to date filter
    date_check.stateChanged.connect(lambda state: date_filter.setEnabled(state == Qt.Checked))
    
    # Add filter button
    filter_btn = create_styled_button("Lọc dữ liệu", "filter", "secondary")
    
    # Layout for filters
    filter_layout.addWidget(search_label)
    filter_layout.addWidget(search_input)
    filter_layout.addSpacing(15)
    filter_layout.addWidget(type_label)
    filter_layout.addWidget(type_combo)
    filter_layout.addSpacing(15)
    filter_layout.addWidget(brand_label)
    filter_layout.addWidget(brand_combo)
    filter_layout.addSpacing(15)
    filter_layout.addWidget(province_label)
    filter_layout.addWidget(province_combo)
    filter_layout.addSpacing(15)
    filter_layout.addWidget(date_label)
    filter_layout.addWidget(date_filter)
    filter_layout.addWidget(date_check)
    filter_layout.addSpacing(15)
    filter_layout.addWidget(filter_btn)
    filter_layout.addStretch()
    
    filter_group.setLayout(filter_layout)
    layout.addWidget(filter_group)
    setup_animation(filter_group, "slide_right")

    # Table group with vehicle list
    table_group = QGroupBox("Danh sách xe")
    table_group.setFont(QFont("Arial", 12, QFont.Bold))
    table_layout = QVBoxLayout()

    main_window.vehicle_table = QTableWidget()
    main_window.vehicle_table.setColumnCount(8)
    main_window.vehicle_table.setHorizontalHeaderLabels([
        "STT", "Biển số", "Chủ xe", "Số điện thoại",
        "Loại xe", "Hãng xe","Tỉnh/Thành phố", "Thời gian đăng ký"
    ])
    main_window.vehicle_table.setAlternatingRowColors(True)
    main_window.vehicle_table.setSelectionBehavior(QAbstractItemView.SelectRows)
    main_window.vehicle_table.setSelectionMode(QAbstractItemView.SingleSelection)
    main_window.vehicle_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
    main_window.vehicle_table.setSortingEnabled(True)
    main_window.vehicle_table.verticalHeader().setVisible(False)

    # Configure column widths
    header = main_window.vehicle_table.horizontalHeader()
    header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # STT
    header.setSectionResizeMode(1, QHeaderView.Stretch)           # Biển số
    header.setSectionResizeMode(2, QHeaderView.Stretch)           # Chủ xe
    header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # SĐT
    header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Loại xe
    header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Hãng xe
    header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Tỉnh/Thành phố
    header.setSectionResizeMode(7, QHeaderView.Stretch)           # Thời gian

    # Improve table header style
    main_window.vehicle_table.horizontalHeader().setStyleSheet(
        f"QHeaderView::section {{ background-color: {MyColor.PRIMARY}; color: {MyColor.WHITE}; padding: 10px; font-weight: bold; }}"
    )

    table_layout.addWidget(main_window.vehicle_table)
    table_group.setLayout(table_layout)
    layout.addWidget(table_group)
    setup_animation(table_group, "slide_up")

    # Action buttons with improved styling
    button_layout = QHBoxLayout()

    # Refresh button
    refresh_btn = create_styled_button("Làm mới danh sách", "refresh", "info")
    refresh_btn.clicked.connect(lambda: refresh_vehicle_list(main_window))

    # Export button
    export_btn = create_styled_button("Xuất danh sách", "export", "success")
    export_btn.setObjectName("exportButton")
    export_btn.clicked.connect(lambda: export_vehicle_list(main_window))

    # Add button - new functionality
    add_btn = create_styled_button("Thêm xe mới", "add", "primary")
    add_btn.clicked.connect(lambda: add_new_vehicle_dialog(main_window))

    # Edit button - new functionality
    edit_btn = create_styled_button("Sửa thông tin", "edit", "primary")
    edit_btn.clicked.connect(lambda: edit_selected_vehicle(main_window))

    # Change history button
    history_btn = create_styled_button("Xem lịch sử", "history", "info")
    history_btn.clicked.connect(lambda: view_vehicle_history(main_window))
    button_layout.addWidget(history_btn)

    # Delete button
    delete_btn = create_styled_button("Xóa xe đã chọn", "delete", "danger")
    delete_btn.setObjectName("deleteButton")
    delete_btn.clicked.connect(lambda: delete_selected_vehicle(main_window))
    
    # Add buttons to layout
    button_layout.addWidget(refresh_btn)
    button_layout.addWidget(export_btn)
    button_layout.addWidget(add_btn)
    button_layout.addWidget(edit_btn)
    button_layout.addWidget(delete_btn)
    layout.addLayout(button_layout)

    # Initial table refresh
    refresh_vehicle_list(main_window)
    
    # Connect search input to filter
    search_input.textChanged.connect(lambda text: filter_vehicle_list(main_window, 
                                                                     search_text=text,
                                                                     vehicle_type=type_combo.currentText(), 
                                                                     brand=brand_combo.currentText(),
                                                                     province=province_combo.currentText(),
                                                                     date=date_filter.date() if date_check.isChecked() else None))
    
    # Connect filters to filter function
    filter_btn.clicked.connect(lambda: filter_vehicle_list(main_window, 
                                                         search_text=search_input.text(),
                                                         vehicle_type=type_combo.currentText(), 
                                                         brand=brand_combo.currentText(),
                                                          province=province_combo.currentText(),
                                                         date=date_filter.date() if date_check.isChecked() else None))
    
    # Store filter widgets for reference
    main_window.list_tab_filters = {
        'search_input': search_input,
        'type_combo': type_combo,
        'brand_combo': brand_combo,
        'province_combo': province_combo,
        'date_filter': date_filter,
        'date_check': date_check
    }

def view_vehicle_history(main_window):
    """Hiển thị lịch sử thay đổi của xe đã chọn"""
    try:
        selected_row = main_window.vehicle_table.currentRow()
        if selected_row >= 0:
            # Lấy ID của xe đã chọn
            vehicle_id = main_window.vehicle_table.item(selected_row, 0).data(Qt.UserRole)
            plate = main_window.vehicle_table.item(selected_row, 1).text()
            
            if not vehicle_id:
                # Trường hợp không lưu ID trực tiếp, tìm theo biển số
                db = DatabaseManager()
                vehicle = db.get_vehicle_by_plate(plate)
                if not vehicle:
                    QMessageBox.warning(
                        main_window,
                        "Lỗi",
                        "Không thể tìm thấy thông tin xe này."
                    )
                    return
                vehicle_id = vehicle.get("id")
            
            # Lấy lịch sử thay đổi
            db = DatabaseManager()
            history_list = db.get_vehicle_history(vehicle_id)
            
            if not history_list:
                QMessageBox.information(
                    main_window,
                    "Thông báo",
                    f"Không có lịch sử thay đổi nào cho xe biển số {plate}."
                )
                return
            
            # Hiển thị dialog lịch sử
            show_history_dialog(main_window, plate, history_list)
        else:
            QMessageBox.warning(
                main_window,
                "Lỗi",
                "Vui lòng chọn xe cần xem lịch sử trong danh sách."
            )
    except Exception as e:
        logging.error(f"Error in view_vehicle_history: {str(e)}")
        QMessageBox.critical(main_window, "Lỗi", f"Có lỗi xảy ra khi xem lịch sử: {str(e)}")

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
    
    # Nút xuất lịch sử
    export_btn = create_styled_button("Xuất lịch sử", "export", "success")
    export_btn.clicked.connect(lambda: export_history(main_window, plate, history_list))
    
    # Layout cho các nút
    btn_layout = QHBoxLayout()
    btn_layout.addWidget(export_btn)
    btn_layout.addWidget(close_btn)
    layout.addLayout(btn_layout)
    
    dialog.exec_()

def export_history(main_window, plate, history_list):
    """Xuất lịch sử thay đổi ra file"""
    try:
        # Hiển thị hộp thoại chọn định dạng xuất
        export_format, ok = QInputDialog.getItem(
            main_window,
            "Xuất lịch sử",
            "Chọn định dạng file:",
            ["CSV", "Excel", "PDF"],
            0,
            False
        )
        
        if not ok:
            return
            
        # Hiển thị hộp thoại lưu file
        file_name, _ = QFileDialog.getSaveFileName(
            main_window,
            "Lưu lịch sử thay đổi",
            f"Lich_su_thay_doi_{plate.replace('-', '_').replace('.', '_')}",
            "CSV Files (*.csv);;Excel Files (*.xlsx);;PDF Files (*.pdf)"
        )
        
        if not file_name:
            return
            
        # Chuẩn bị dữ liệu xuất
        export_data = []
        for i, history in enumerate(history_list):
            change_type = history.get("change_type", "")
            change_type_text = {
                "ADD": "Thêm mới",
                "UPDATE": "Cập nhật",
                "DELETE": "Xóa"
            }.get(change_type, change_type)
            
            export_data.append({
                "STT": i + 1,
                "Loại thay đổi": change_type_text,
                "Thời gian": history.get("change_time", ""),
                "Mô tả": history.get("description", "")
            })
        
        # Xuất dữ liệu theo định dạng
        if export_format == "CSV" or file_name.endswith('.csv'):
            import csv
            with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=["STT", "Loại thay đổi", "Thời gian", "Mô tả"])
                writer.writeheader()
                writer.writerows(export_data)
                
        elif export_format == "Excel" or file_name.endswith('.xlsx'):
            import pandas as pd
            df = pd.DataFrame(export_data)
            df.to_excel(file_name, index=False)
            
        elif export_format == "PDF" or file_name.endswith('.pdf'):
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet
            
            doc = SimpleDocTemplate(file_name, pagesize=letter)
            elements = []
            
            # Tiêu đề
            styles = getSampleStyleSheet()
            title = Paragraph(f"LỊCH SỬ THAY ĐỔI XE BIỂN SỐ: {plate}", styles['Heading1'])
            elements.append(title)
            elements.append(Spacer(1, 12))
            
            # Dữ liệu bảng
            data = [["STT", "Loại thay đổi", "Thời gian", "Mô tả"]]
            for item in export_data:
                data.append([item["STT"], item["Loại thay đổi"], item["Thời gian"], item["Mô tả"]])
            
            # Tạo bảng
            table = Table(data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ALIGN', (0, 0), (0, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            elements.append(table)
            
            # Tạo PDF
            doc.build(elements)
        
        QMessageBox.information(
            main_window,
            "Xuất thành công",
            f"Đã xuất lịch sử thay đổi ra file: {file_name}"
        )
            
    except Exception as e:
        logging.error(f"Error exporting history: {str(e)}")
        QMessageBox.critical(main_window, "Lỗi", f"Có lỗi xảy ra khi xuất lịch sử: {str(e)}")
        
def refresh_vehicle_list(main_window):
    """Refresh the vehicle list table with current data"""
    try:
        table = main_window.vehicle_table
        table.setRowCount(0)

        # Lấy dữ liệu từ database
        db = DatabaseManager()
        vehicles = db.search_vehicles()
        
        # Cập nhật vehicle_data để tương thích với code hiện tại
        main_window.vehicle_data = vehicles

        for i, vehicle in enumerate(vehicles):
            row_position = table.rowCount()
            table.insertRow(row_position)

            index_item = QTableWidgetItem(str(i + 1))
            index_item.setTextAlignment(Qt.AlignCenter)
            index_item.setData(Qt.UserRole, vehicle.get("id"))
            
            plate_item = QTableWidgetItem(vehicle["plate"])
            plate_item.setFont(QFont("Arial", 10, QFont.Bold))

            owner_item = QTableWidgetItem(vehicle["owner"])
            phone_item = QTableWidgetItem(vehicle["phone"])
            type_item = QTableWidgetItem(vehicle["type"])
            brand_item = QTableWidgetItem(vehicle["brand"])
            province_item = QTableWidgetItem(vehicle.get("province", ""))
            date_item = QTableWidgetItem(vehicle["timestamp"])

            if i % 2 == 0:
                row_color = QBrush(QColor(MyColor.BACKGROUND))
            else:
                row_color = QBrush(QColor(MyColor.WHITE))

            for col, item in enumerate([index_item, plate_item, owner_item,
                                        phone_item, type_item, brand_item,province_item, date_item]):
                item.setBackground(row_color)
                table.setItem(row_position, col, item)
        
        # Refresh status information
        if hasattr(main_window, 'statusBar'):
            main_window.statusBar().showMessage(f"Tổng số xe đã đăng ký: {len(vehicles)}")
    except Exception as e:
        logging.error(f"Error refreshing vehicle list: {str(e)}")
        QMessageBox.critical(main_window, "Lỗi", f"Không thể tải danh sách xe: {str(e)}")


def filter_vehicle_list(main_window, search_text="", vehicle_type="Tất cả", brand="Tất cả", province="Tất cả", date=None):
    """Filter the vehicle list based on search criteria"""
    try:
        table = main_window.vehicle_table
        table.setRowCount(0)
        
        # Sử dụng database manager để lọc dữ liệu
        db = DatabaseManager()
        
        # Chuyển đổi định dạng ngày nếu cần
        date_str = None
        if date:
            date_str = date.toString("yyyy-MM-dd")
        
        # Lấy dữ liệu đã lọc từ database
        filtered_vehicles = db.search_vehicles(
            search_text=search_text if search_text else None,
            vehicle_type=vehicle_type if vehicle_type != "Tất cả" else None,
            brand=brand if brand != "Tất cả" else None,
            province=province if province != "Tất cả" else None,
            date=date_str
        )
        
        # Hiển thị kết quả
        for i, vehicle in enumerate(filtered_vehicles):
            row_position = table.rowCount()
            table.insertRow(row_position)
            
            index_item = QTableWidgetItem(str(i + 1))
            index_item.setTextAlignment(Qt.AlignCenter)
            
            plate_item = QTableWidgetItem(vehicle["plate"])
            plate_item.setFont(QFont("Arial", 10, QFont.Bold))
            
            owner_item = QTableWidgetItem(vehicle["owner"])
            phone_item = QTableWidgetItem(vehicle["phone"])
            type_item = QTableWidgetItem(vehicle["type"])
            brand_item = QTableWidgetItem(vehicle["brand"])
            province_item = QTableWidgetItem(vehicle.get("province", ""))
            date_item = QTableWidgetItem(vehicle["timestamp"])
            
            if i % 2 == 0:
                row_color = QBrush(QColor(MyColor.BACKGROUND))
            else:
                row_color = QBrush(QColor(MyColor.WHITE))
            
            for col, item in enumerate([index_item, plate_item, owner_item,
                                        phone_item, type_item, brand_item,province_item, date_item]):
                item.setBackground(row_color)
                table.setItem(row_position, col, item)
        
        # Lấy tổng số xe để hiển thị thống kê
        all_vehicles_count = len(db.search_vehicles())
        
        # Update status bar with filter information
        if hasattr(main_window, 'statusBar'):
            main_window.statusBar().showMessage(f"Hiển thị {len(filtered_vehicles)} trên tổng số {all_vehicles_count} xe đã đăng ký")
    except Exception as e:
        logging.error(f"Error filtering vehicle list: {str(e)}")
        QMessageBox.warning(main_window, "Lỗi", f"Không thể lọc dữ liệu: {str(e)}")


def delete_selected_vehicle(main_window):
    """Delete the selected vehicle from the list"""
    try:
        selected_row = main_window.vehicle_table.currentRow()
        if selected_row >= 0:
            # Get the plate number for confirmation
            plate = main_window.vehicle_table.item(selected_row, 1).text()
            
            # Confirm deletion
            confirm = QMessageBox.question(
                main_window,
                "Xác nhận xóa",
                f"Bạn có chắc chắn muốn xóa xe có biển số '{plate}'?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if confirm == QMessageBox.Yes:
                # Sử dụng database manager để xóa xe
                db = DatabaseManager()
                success, message = db.delete_vehicle(plate)
                
                if success:
                    # Refresh the list
                    refresh_vehicle_list(main_window)
                    
                    QMessageBox.information(
                        main_window,
                        "Xóa thành công",
                        f"Đã xóa xe có biển số '{plate}' khỏi danh sách."
                    )
                else:
                    QMessageBox.warning(
                        main_window,
                        "Lỗi xóa",
                        f"Không thể xóa xe: {message}"
                    )
        else:
            QMessageBox.warning(
                main_window,
                "Lỗi",
                "Vui lòng chọn xe cần xóa trong danh sách."
            )
    except Exception as e:
        logging.error(f"Error in delete_selected_vehicle: {str(e)}")
        QMessageBox.critical(main_window, "Lỗi", f"Có lỗi xảy ra khi xóa xe: {str(e)}")


def export_vehicle_list(main_window):
    """Export the vehicle list to a CSV or Excel file"""
    try:
        # Ask for file format
        format_dialog = QDialog(main_window)
        format_dialog.setWindowTitle("Chọn định dạng xuất")
        format_dialog.setMinimumWidth(300)
        
        format_layout = QVBoxLayout(format_dialog)
        format_layout.addWidget(QLabel("Chọn định dạng file:"))
        
        csv_btn = QPushButton("CSV (.csv)")
        csv_btn.setIcon(AppIcons.get_icon("file-csv", MyColor.INFO))
        
        excel_btn = QPushButton("Excel (.xlsx)")
        excel_btn.setIcon(AppIcons.get_icon("file-excel", MyColor.SUCCESS))
        
        html_btn = QPushButton("HTML (.html)")
        html_btn.setIcon(AppIcons.get_icon("file-code", MyColor.PRIMARY))
        
        format_layout.addWidget(csv_btn)
        format_layout.addWidget(excel_btn)
        format_layout.addWidget(html_btn)
        
        # Function to export as CSV
        def export_as_csv():
            format_dialog.close()
            filename, _ = QFileDialog.getSaveFileName(
                main_window, 
                "Lưu danh sách xe", 
                "", 
                "CSV files (*.csv)"
            )
            if filename:
                try:
                    import csv
                    with open(filename, 'w', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        # Write header
                        writer.writerow([
                            "STT", "Biển số", "Chủ xe", "Số điện thoại",
                            "Loại xe", "Hãng xe", "Tỉnh/Thành phố", "Thời gian đăng ký"
                        ])
                        
                        # Write data
                        for i, vehicle in enumerate(main_window.vehicle_data):
                            writer.writerow([
                                i+1,
                                vehicle.get("plate", ""),
                                vehicle.get("owner", ""),
                                vehicle.get("phone", ""),
                                vehicle.get("type", ""),
                                vehicle.get("brand", ""),
                                vehicle.get("province", ""),
                                vehicle.get("timestamp", "")
                            ])
                    
                    QMessageBox.information(
                        main_window,
                        "Xuất thành công",
                        f"Đã xuất danh sách xe ra file CSV: {filename}"
                    )
                except Exception as e:
                    logging.error(f"Error exporting to CSV: {str(e)}")
                    QMessageBox.warning(
                        main_window,
                        "Lỗi",
                        f"Không thể xuất dữ liệu ra file CSV: {str(e)}"
                    )
        
        # Function to export as Excel
        def export_as_excel():
            format_dialog.close()
            
            filename, _ = QFileDialog.getSaveFileName(
                main_window, 
                "Lưu danh sách xe", 
                "", 
                "Excel files (*.xlsx)"
            )
            
            if filename:
                # Sử dụng database manager để xuất dữ liệu
                from database.vehicle_model import export_to_excel
                
                if export_to_excel(main_window.vehicle_data, filename):
                    QMessageBox.information(
                        main_window,
                        "Xuất thành công",
                        f"Đã xuất danh sách xe ra file Excel: {filename}"
                    )
                else:
                    QMessageBox.warning(
                        main_window,
                        "Lỗi",
                        "Không thể xuất dữ liệu ra file Excel."
                    )
        
        # Function to export as HTML
        def export_as_html():
            format_dialog.close()
            
            filename, _ = QFileDialog.getSaveFileName(
                main_window, 
                "Lưu danh sách xe", 
                "", 
                "HTML files (*.html)"
            )
            
            if filename:
                # Sử dụng database manager để xuất dữ liệu
                from database.vehicle_model import export_to_html
                
                if export_to_html(main_window.vehicle_data, filename):
                    QMessageBox.information(
                        main_window,
                        "Xuất thành công",
                        f"Đã xuất danh sách xe ra file HTML: {filename}"
                    )
                else:
                    QMessageBox.warning(
                        main_window,
                        "Lỗi",
                        "Không thể xuất dữ liệu ra file HTML."
                    )
        
        # Connect buttons to export functions
        csv_btn.clicked.connect(export_as_csv)
        excel_btn.clicked.connect(export_as_excel)
        html_btn.clicked.connect(export_as_html)
        
        format_dialog.exec_()
    except Exception as e:
        logging.error(f"Error in export_vehicle_list: {str(e)}")
        QMessageBox.critical(main_window, "Lỗi", f"Có lỗi xảy ra khi xuất danh sách: {str(e)}")


def add_new_vehicle_dialog(main_window):
    """Show dialog to add a new vehicle directly from the list tab"""
    try:
        dialog = QDialog(main_window)
        dialog.setWindowTitle("Thêm xe mới")
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout(dialog)
        
        # Owner info
        owner_group = QGroupBox("Thông tin chủ xe")
        owner_form = QFormLayout()
        
        owner_name_input = QLineEdit()
        owner_name_input.setPlaceholderText("Nhập họ tên chủ xe")
        
        owner_phone_input = QLineEdit()
        owner_phone_input.setPlaceholderText("Nhập số điện thoại")
        
        owner_form.addRow("Họ tên:", owner_name_input)
        owner_form.addRow("Số điện thoại:", owner_phone_input)
        owner_group.setLayout(owner_form)
        
        # Vehicle info
        vehicle_group = QGroupBox("Thông tin xe")
        vehicle_form = QFormLayout()
        
        plate_input = QLineEdit()
        plate_input.setPlaceholderText("Nhập biển số xe")
        # Thêm validator để chỉ cho phép ký tự chữ và số, không có khoảng trắng hoặc ký tự đặc biệt
        from PyQt5.QtGui import QRegExpValidator
        from PyQt5.QtCore import QRegExp

        # Regex chỉ cho phép chữ cái và số
        reg_ex = QRegExp("^[A-Za-z0-9]+$")
        plate_validator = QRegExpValidator(reg_ex)
        plate_input.setValidator(plate_validator)

        # Kết nối sự kiện textChanged để tự động chuyển đổi sang chữ in hoa
        plate_input.textChanged.connect(lambda text: plate_input.setText(text.upper()))
        
        vehicle_type_input = QComboBox()
        vehicle_type_input.addItems(["Xe ô tô", "Xe kháchkhách", "Xe máy", "Khác"])
        
        brand_input = QComboBox()
        brand_input.addItems(["Toyota", "Honda", "Mazda", "Ford", "Hyundai", 
        "Kia", "Mercedes-Benz", "BMW", "Audi", "Chevrolet",
        "Nissan", "Mitsubishi", "Suzuki", "Yamaha", "Khác"])
        
        color_input = QLineEdit()
        color_input.setPlaceholderText("Nhập màu xe")
        # Thêm ComboBox province_input ở đây
        province_input = QComboBox()
        province_input.addItems([
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
        notes_input = QLineEdit()
        notes_input.setPlaceholderText("Ghi chú (không bắt buộc)")
        
        vehicle_form.addRow("Biển số xe:", plate_input)
        vehicle_form.addRow("Loại xe:", vehicle_type_input)
        vehicle_form.addRow("Hãng xe:", brand_input)
        vehicle_form.addRow("Màu xe:", color_input)
        vehicle_form.addRow("Tỉnh/Thành phố:", province_input) 
        vehicle_form.addRow("Ghi chú:", notes_input)
        vehicle_group.setLayout(vehicle_form)
        
        # Add to layout
        layout.addWidget(owner_group)
        layout.addWidget(vehicle_group)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        save_btn = create_styled_button("Lưu", "save", "success")
        cancel_btn = create_styled_button("Hủy", "cancel", "danger")
        
        buttons_layout.addWidget(save_btn)
        buttons_layout.addWidget(cancel_btn)
        layout.addLayout(buttons_layout)
        
        # Handle save
        def save_vehicle():
            # Validate
            if not (owner_name_input.text() and owner_phone_input.text() and plate_input.text()):
                QMessageBox.warning(dialog, "Lỗi", "Vui lòng điền đầy đủ thông tin bắt buộc!")
                return
            
            # Create new vehicle entry
            try:
                # Sử dụng database manager để thêm xe
                db = DatabaseManager()
                success, result = db.add_vehicle(
                    plate=plate_input.text(),
                    owner=owner_name_input.text(),
                    phone=owner_phone_input.text(),
                    vehicle_type=vehicle_type_input.currentText(),
                    brand=brand_input.currentText(),
                    color=color_input.text(),
                    province=province_input.currentText(),
                    notes=notes_input.text()
                )
                
                if success:
                    # Refresh the list
                    refresh_vehicle_list(main_window)
                    
                    QMessageBox.information(dialog, "Thành công", "Đã thêm xe mới vào hệ thống!")
                    dialog.accept()
                else:
                    QMessageBox.critical(dialog, "Lỗi", f"Không thể thêm xe: {result}")
                
            except Exception as e:
                QMessageBox.critical(dialog, "Lỗi", f"Không thể thêm xe: {str(e)}")
        
        # Connect buttons
        save_btn.clicked.connect(save_vehicle)
        cancel_btn.clicked.connect(dialog.reject)
        
        dialog.exec_()
    except Exception as e:
        logging.error(f"Error in add_new_vehicle_dialog: {str(e)}")
        QMessageBox.critical(main_window, "Lỗi", f"Có lỗi xảy ra: {str(e)}")