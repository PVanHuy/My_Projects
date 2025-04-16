from PyQt5.QtWidgets import (QTabWidget, QWidget, QVBoxLayout, QApplication, 
                           QMainWindow, QDesktopWidget, QSplashScreen, QLabel,
                           QProgressBar, QFrame, QMessageBox)
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QSize
from PyQt5.QtGui import QColor, QPainter
import sys
import os
import logging

from ui.register_tab import setup_register_tab
from ui.list_tab import setup_list_tab
from ui.search_tab import setup_search_tab
from ui.style import apply_stylesheet, setup_animation
from colors.my_colors import MyColor
from utils.app_icons import AppIcons
from utils.theme_manager import theme_manager
from utils.theme_switch import ThemeSwitch
from database.db_manager import DatabaseManager

# Cấu hình logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

def center_window(window):
    """Center the window on the screen"""
    qr = window.frameGeometry()
    cp = QDesktopWidget().availableGeometry().center()
    qr.moveCenter(cp)
    window.move(qr.topLeft())

def show_splash_screen(app):
    """Show a splash screen while loading application"""
    splash_pix = QPixmap("resources/icons/splash.png")
    
    if splash_pix.isNull():
        # Create a default splash screen if image is not found
        splash_pix = QPixmap(600, 400)
        splash_pix.fill(QColor(MyColor.PRIMARY))
        
        # We can also draw on the pixmap if needed
        painter = QPainter(splash_pix)
        painter.setFont(QFont("Arial", 30, QFont.Bold))
        painter.setPen(QColor(MyColor.WHITE))
        painter.drawText(splash_pix.rect(), Qt.AlignCenter, "Hệ thống quản lý đăng ký xe")
        painter.end()
        
    splash = QSplashScreen(splash_pix)

    # Add styling to splash screen
    splash.setStyleSheet(f"""
        QSplashScreen {{
            border: 2px solid {MyColor.SECONDARY};
            border-radius: 10px;
        }}
    """)
    
    # Add content to splash screen
    splash_content = QWidget(splash)
    splash_layout = QVBoxLayout(splash_content)
    splash_layout.setContentsMargins(0, splash_pix.height() - 100, 0, 20)
    
    # App title
    splash_label = QLabel("Hệ thống quản lý đăng ký xe v1.0", splash)
    splash_label.setGeometry(0, splash_pix.height() - 90, splash_pix.width(), 30)
    splash_label.setAlignment(Qt.AlignCenter)
    splash_label.setStyleSheet(f"""
        font-family: 'Arial';
        font-size: 18px;
        font-weight: bold;
        color: {MyColor.WHITE};
    """)
    
    # Progress bar
    splash_progress = QProgressBar(splash)
    splash_progress.setGeometry(50, splash_pix.height() - 50, splash_pix.width() - 100, 20)
    splash_progress.setRange(0, 100)
    splash_progress.setValue(0)
    splash_progress.setAlignment(Qt.AlignCenter)
    splash_progress.setFormat("Đang khởi động... %p%")
    splash_progress.setStyleSheet(f"""
        QProgressBar {{
            border: 1px solid {MyColor.WHITE};
            border-radius: 5px;
            background-color: {MyColor.BACKGROUND};
            text-align: center;
            padding: 1px;
            font-weight: bold;
        }}
        
        QProgressBar::chunk {{
            background-color: {MyColor.ACCENT};
            border-radius: 4px;
        }}
    """)
    
    # Show splash and start progress updates
    splash.show()
    app.processEvents()
    
    # Simulate loading process
    def update_progress():
        current = splash_progress.value()
        if current < 100:
            splash_progress.setValue(current + 5)
            QTimer.singleShot(100, update_progress)
    
    update_progress()
    
    return splash, splash_progress

def setup_main_window(window):
    """Set up the main application window with tabs and styling"""
    try:
        window.setWindowTitle("Hệ thống quản lý đăng ký xe")
        window.setWindowIcon(AppIcons.get_icon("app"))
        window.resize(1200, 800)
        
        # Khởi tạo database và lấy dữ liệu mẫu
        db = DatabaseManager()
        
        # Kiểm tra và sửa lỗi database nếu cần
        success, message = db.fix_database_errors()
        if not success:
            logging.warning(f"Database fix issue: {message}")
        
        # Nạp dữ liệu từ database
        window.vehicle_data = db.search_vehicles()
        
        # Set up central widget
        central_widget = QWidget()
        window.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # Set up tab widget with improved styling
        tab_widget = QTabWidget()
        tab_widget.setDocumentMode(True)
        tab_widget.setElideMode(Qt.ElideRight)
        tab_widget.setMovable(True)
        tab_widget.setTabPosition(QTabWidget.North)
        
        # Animation for tab changes
        def animate_tab_change(index):
            current_widget = tab_widget.widget(index)
            
            # Create an opacity effect for smooth fade transition
            opacity_effect = QPropertyAnimation(current_widget, b"windowOpacity")
            opacity_effect.setDuration(400)
            opacity_effect.setStartValue(0.3)
            opacity_effect.setEndValue(1.0)
            opacity_effect.setEasingCurve(QEasingCurve.OutCubic)
            opacity_effect.start()
            
            window.tab_animation = opacity_effect
            
            # Reset search tab when switching to it (index 2)
            if index == 2 and hasattr(window, 'reset_search_tab'):
                # Delay slightly to ensure UI is ready
                QTimer.singleShot(100, window.reset_search_tab)
                
        # Create tab widgets
        register_tab = QWidget()
        list_tab = QWidget()
        search_tab = QWidget()
        
        # Apply smooth transition effect
        for tab in [register_tab, list_tab, search_tab]:
            tab.setAutoFillBackground(True)
        
        # Set up tabs with improved layouts
        setup_register_tab(register_tab, window)
        setup_list_tab(list_tab, window)
        setup_search_tab(search_tab, window)
        
        # Add tabs with improved icons from QtAwesome
        tab_widget.addTab(register_tab, AppIcons.get_icon("register"), "Đăng ký xe")
        tab_widget.addTab(list_tab, AppIcons.get_icon("list"), "Danh sách xe")
        tab_widget.addTab(search_tab, AppIcons.get_icon("search"), "Tra cứu biển số")
        
        # Connect tab change event to animation
        tab_widget.currentChanged.connect(animate_tab_change)
        main_layout.addWidget(tab_widget)
        window.tab_widget = tab_widget
        
        # Thêm nút chuyển đổi theme ở góc phải trên
        theme_switch = ThemeSwitch(window)
        window.theme_switch = theme_switch
        
        # Đặt vị trí ban đầu ở góc phải trên
        def update_switch_position():
            theme_switch.move(window.width() - theme_switch.width() - 20, 15)
        
        # Cập nhật vị trí khi cửa sổ thay đổi kích thước
        original_resize_event = window.resizeEvent
        def resize_event_handler(event):
            if original_resize_event:
                original_resize_event(event)
            update_switch_position()
        
        window.resizeEvent = resize_event_handler
        
        # Kết nối sự kiện chuyển đổi theme
        theme_switch.toggled.connect(lambda checked: apply_stylesheet(window))
        
        # Hiển thị ban đầu
        theme_switch.raise_()
        update_switch_position()
        
        # Apply stylesheet and center window
        apply_stylesheet(window)
        center_window(window)
        
        # Create status bar with version info
        status_bar = window.statusBar()
        status_bar.showMessage("Hệ thống quản lý đăng ký xe - Phiên bản 1.0")
        status_bar.setStyleSheet(f"color: {MyColor.TEXT_SECONDARY}; padding: 5px;")
    except Exception as e:
        logging.error(f"Error in setup_main_window: {str(e)}")
        QMessageBox.critical(window, "Lỗi khởi tạo", f"Lỗi khi thiết lập cửa sổ chính: {str(e)}")

def initialize_application():
    """Initialize the main application"""
    import sys
    from PyQt5.QtWidgets import QApplication, QMainWindow
    import logging
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("app.log"),
            logging.StreamHandler()
        ]
    )
    
    # Catch unhandled exceptions
    def exception_hook(exc_type, exc_value, exc_traceback):
        logging.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
    
    sys.excepthook = exception_hook
    
    try:
        app = QApplication(sys.argv)
        
        # Set application style to Fusion for consistent look across platforms
        app.setStyle("Fusion")
        
        # Show splash screen
        splash, progress_bar = show_splash_screen(app)
        
        # Create main window
        main_window = QMainWindow()
        
        # Schedule setup after short delay for splash screen to display
        QTimer.singleShot(1500, lambda: setup_main_window(main_window))
        QTimer.singleShot(2000, lambda: main_window.show())
        QTimer.singleShot(2100, splash.close)
        
        return app, main_window
    except Exception as e:
        logging.error(f"Error initializing application: {str(e)}")
        # Create minimal fallback app in case of error
        app = QApplication(sys.argv) if not QApplication.instance() else QApplication.instance()
        main_window = QMainWindow()
        main_window.setWindowTitle("Error initializing application")
        main_window.resize(800, 600)
        
        # Show error dialog
        QMessageBox.critical(
            None,
            "Lỗi khởi động",
            f"Không thể khởi động ứng dụng: {str(e)}\n\nVui lòng kiểm tra lại cài đặt."
        )
        
        return app, main_window

if __name__ == "__main__":
    app, main_window = initialize_application()
    sys.exit(app.exec_())