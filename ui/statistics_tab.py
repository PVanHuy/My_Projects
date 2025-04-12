import qtawesome as qta
from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QComboBox, 
    QPushButton, QGroupBox, QFrame, QGridLayout
)
from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtCore import Qt, QDate, QSize
from colors.my_colors import MyColor
from ui.style import setup_animation
def setup_statistics_tab(tab, main_window):
    layout = QVBoxLayout(tab)
    layout.setSpacing(20)
    title_layout = QHBoxLayout()
    icon_label = QLabel()
    icon_label.setPixmap(QIcon("resources/icons/statistics.png").pixmap(QSize(48, 48)))
    title = QLabel("THỐNG KÊ XE ĐĂNG KÝ")
    title.setFont(QFont("Arial", 22, QFont.Bold))
    title.setStyleSheet(f"color: {MyColor.PRIMARY};")
    title_layout.addWidget(icon_label)
    title_layout.addWidget(title)
    title_layout.addStretch()
    layout.addLayout(title_layout)
    filter_group = QGroupBox("Tùy chọn thống kê")
    filter_group.setFont(QFont("Arial", 12, QFont.Bold))
    filter_layout = QHBoxLayout()
    period_label = QLabel("Thời gian:")
    period_label.setFont(QFont("Arial", 10))
    period_combo = QComboBox()
    period_combo.addItems(["Hôm nay", "Tuần này", "Tháng này", "Năm nay", "Tất cả"])
    period_combo.setMinimumHeight(35)
    type_label = QLabel("Loại xe:")
    type_label.setFont(QFont("Arial", 10))
    type_combo = QComboBox()
    type_combo.addItems(["Tất cả", "Ô tô", "Xe máy", "Xe tải", "Xe khách"])
    type_combo.setMinimumHeight(35)
    apply_btn = QPushButton("Áp dụng")
    apply_btn.setIcon(QIcon("resources/icons/refresh.png"))
    apply_btn.setMinimumHeight(35)
    apply_btn.setStyleSheet(f"background-color: {MyColor.SECONDARY};")
    filter_layout.addWidget(period_label)
    filter_layout.addWidget(period_combo)
    filter_layout.addSpacing(20)
    filter_layout.addWidget(type_label)
    filter_layout.addWidget(type_combo)
    filter_layout.addSpacing(20)
    filter_layout.addWidget(apply_btn)
    filter_layout.addStretch()
    filter_group.setLayout(filter_layout)
    layout.addWidget(filter_group)
    setup_animation(filter_group, "slide_right")
    summary_layout = QHBoxLayout()
    def create_summary_card(title, value, icon_name, color):
        card = QFrame()
        card.setFrameShape(QFrame.StyledPanel)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {MyColor.WHITE};
                border-radius: 10px;
                border: 1px solid {MyColor.GRAY};
            }}
        """)
        
        card_layout = QVBoxLayout(card)
        header_layout = QHBoxLayout()
        icon = QLabel()
        icon.setPixmap(QIcon(f"resources/icons/{icon_name}.png").pixmap(QSize(24, 24)))
        header_title = QLabel(title)
        header_title.setFont(QFont("Arial", 10, QFont.Bold))
        header_title.setStyleSheet(f"color: {MyColor.TEXT_SECONDARY};")
        header_layout.addWidget(icon)
        header_layout.addWidget(header_title)
        header_layout.addStretch()
        value_label = QLabel(value)
        value_label.setFont(QFont("Arial", 24, QFont.Bold))
        value_label.setAlignment(Qt.AlignCenter)
        value_label.setStyleSheet(f"color: {color};")
        
        card_layout.addLayout(header_layout)
        card_layout.addWidget(value_label)
        
        return card
    
    total_card = create_summary_card("Tổng số xe", "150", "car", MyColor.PRIMARY)
    today_card = create_summary_card("Đăng ký hôm nay", "12", "calendar", MyColor.SUCCESS)
    car_card = create_summary_card("Ô tô", "95", "car", MyColor.ACCENT)
    bike_card = create_summary_card("Xe máy", "55", "motorcycle", MyColor.INFO)
    
    summary_layout.addWidget(total_card)
    summary_layout.addWidget(today_card)
    summary_layout.addWidget(car_card)
    summary_layout.addWidget(bike_card)
    
    layout.addLayout(summary_layout)
    chart_group = QGroupBox("Biểu đồ thống kê")
    chart_group.setFont(QFont("Arial", 12, QFont.Bold))
    chart_layout = QVBoxLayout()
    
    chart_placeholder = QLabel("Biểu đồ thống kê đăng ký xe theo thời gian")
    chart_placeholder.setAlignment(Qt.AlignCenter)
    chart_placeholder.setStyleSheet(f"""
        background-color: {MyColor.BACKGROUND};
        border: 1px dashed {MyColor.GRAY};
        border-radius: 10px;
        padding: 40px;
        color: {MyColor.TEXT_SECONDARY};
    """)
    chart_placeholder.setMinimumHeight(300)
    
    chart_layout.addWidget(chart_placeholder)
    chart_group.setLayout(chart_layout)
    
    layout.addWidget(chart_group)
    setup_animation(chart_group, "fade")
    export_layout = QHBoxLayout()
    
    export_btn = QPushButton("Xuất báo cáo thống kê")
    export_btn.setIcon(QIcon("resources/icons/export.png"))
    export_btn.setMinimumHeight(40)
    export_btn.setStyleSheet(f"background-color: {MyColor.SECONDARY};")
    
    print_btn = QPushButton("In báo cáo")
    print_btn.setIcon(QIcon("resources/icons/print.png"))
    print_btn.setMinimumHeight(40)
    
    export_layout.addWidget(export_btn)
    export_layout.addWidget(print_btn)
    export_layout.addStretch()
    
    layout.addLayout(export_layout)
    def update_statistics():
        for widget in [total_card, today_card, car_card, bike_card]:
            setup_animation(widget, "fade")
    
    apply_btn.clicked.connect(update_statistics)