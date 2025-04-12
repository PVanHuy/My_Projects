from PyQt5.QtWidgets import QMainWindow, QAction, QToolBar, QMenu
from PyQt5.QtCore import QSize, Qt, QTimer
from PyQt5.QtGui import QIcon

from ui.main_window import setup_main_window
from ui.style import apply_stylesheet
from utils.theme_manager import theme_manager
from utils.app_icons import AppIcons

class LicensePlateApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hệ thống quản lý đăng ký xe")
        self.setGeometry(100, 100, 1200, 800)
        self.setMinimumSize(QSize(1000, 700))
        
        # Initialize sample data
        self.vehicle_data = []
        
        # Set up the main window UI
        setup_main_window(self)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create toolbar
        self.create_toolbar()
        
        # Apply initial stylesheet
        self.apply_theme()
        
        # Connect theme manager signal to update UI when theme changes
        theme_manager.themeChanged.connect(self.on_theme_changed)
    
    def create_menu_bar(self):
        """Create the application menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        # Add actions to File menu
        new_action = QAction("&Thêm xe mới", self)
        new_action.setIcon(AppIcons.get_icon("add"))
        new_action.setShortcut("Ctrl+N")
        new_action.setStatusTip("Thêm xe mới vào hệ thống")
        new_action.triggered.connect(self.on_add_new_vehicle)
        file_menu.addAction(new_action)
        
        export_action = QAction("&Xuất danh sách", self)
        export_action.setIcon(AppIcons.get_icon("export"))
        export_action.setShortcut("Ctrl+E")
        export_action.setStatusTip("Xuất danh sách xe ra file")
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("&Thoát", self)
        exit_action.setIcon(AppIcons.get_icon("logout"))
        exit_action.setShortcut("Ctrl+Q")
        exit_action.setStatusTip("Thoát ứng dụng")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("&Chỉnh sửa")
        
        # Add actions to Edit menu
        settings_action = QAction("&Cài đặt", self)
        settings_action.setIcon(AppIcons.get_icon("settings"))
        settings_action.setStatusTip("Mở cài đặt ứng dụng")
        edit_menu.addAction(settings_action)
        
        # Theme submenu
        theme_menu = QMenu("&Giao diện", self)
        theme_menu.setIcon(AppIcons.get_icon("palette"))
        
        light_theme_action = QAction("&Nền sáng", self)
        light_theme_action.setCheckable(True)
        light_theme_action.setChecked(theme_manager.current_theme() == theme_manager.LIGHT)
        light_theme_action.triggered.connect(lambda: self.change_theme(theme_manager.LIGHT))
        
        dark_theme_action = QAction("&Nền tối", self)
        dark_theme_action.setCheckable(True)
        dark_theme_action.setChecked(theme_manager.current_theme() == theme_manager.DARK)
        dark_theme_action.triggered.connect(lambda: self.change_theme(theme_manager.DARK))
        
        # Group theme actions
        self.theme_actions = [light_theme_action, dark_theme_action]
        
        theme_menu.addAction(light_theme_action)
        theme_menu.addAction(dark_theme_action)
        edit_menu.addMenu(theme_menu)
        
        # Help menu
        help_menu = menubar.addMenu("&Trợ giúp")
        
        about_action = QAction("&Giới thiệu", self)
        about_action.setIcon(AppIcons.get_icon("info"))
        about_action.setStatusTip("Thông tin về ứng dụng")
        help_menu.addAction(about_action)
        
        help_action = QAction("&Hướng dẫn sử dụng", self)
        help_action.setIcon(AppIcons.get_icon("help"))
        help_action.setShortcut("F1")
        help_action.setStatusTip("Xem hướng dẫn sử dụng")
        help_menu.addAction(help_action)
    
    def create_toolbar(self):
        """Create the application toolbar"""
        # Main toolbar
        self.toolbar = QToolBar("Main Toolbar")
        self.toolbar.setMovable(False)
        self.toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(Qt.TopToolBarArea, self.toolbar)
        
        # Add actions to toolbar
        self.toolbar.addAction(AppIcons.get_icon("register"), "Đăng ký xe mới", 
                              lambda: self.tab_widget.setCurrentIndex(0))
        self.toolbar.addAction(AppIcons.get_icon("list"), "Danh sách xe", 
                              lambda: self.tab_widget.setCurrentIndex(1))
        self.toolbar.addAction(AppIcons.get_icon("search"), "Tra cứu biển số", 
                              lambda: self.tab_widget.setCurrentIndex(2))
        
        self.toolbar.addSeparator()
        
        self.toolbar.addAction(AppIcons.get_icon("add"), "Thêm xe mới", self.on_add_new_vehicle)
        self.toolbar.addAction(AppIcons.get_icon("refresh"), "Làm mới dữ liệu", self.refresh_data)
        
        self.toolbar.addSeparator()
        
        # Theme toggle button
        self.theme_toggle_action = QAction("Chuyển đổi giao diện", self)
        self.update_theme_icon()
        self.theme_toggle_action.triggered.connect(theme_manager.toggle_theme)
        self.toolbar.addAction(self.theme_toggle_action)
    
    def update_theme_icon(self):
        """Update the theme toggle button icon based on current theme"""
        if theme_manager.current_theme() == theme_manager.LIGHT:
            self.theme_toggle_action.setIcon(AppIcons.get_icon("moon"))
            self.theme_toggle_action.setStatusTip("Chuyển sang chế độ nền tối")
        else:
            self.theme_toggle_action.setIcon(AppIcons.get_icon("sun"))
            self.theme_toggle_action.setStatusTip("Chuyển sang chế độ nền sáng")
    
    def change_theme(self, theme_name):
        """Change the application theme"""
        # Update checkable actions
        for action in self.theme_actions:
            if action.text() == "&Nền sáng" and theme_name == theme_manager.LIGHT:
                action.setChecked(True)
            elif action.text() == "&Nền tối" and theme_name == theme_manager.DARK:
                action.setChecked(True)
            else:
                action.setChecked(False)
        
        # Set the theme
        theme_manager.set_theme(theme_name)
    
    def on_theme_changed(self, theme_name):
        """Handle theme change event"""
        self.update_theme_icon()
        self.apply_theme()
    
    def apply_theme(self):
        """Apply the current theme to the application"""
        apply_stylesheet(self)
        
        # Force repaint of all widgets
        self.update()
        
        # Update status bar with theme info
        if hasattr(self, 'statusBar'):
            current_theme = "Nền sáng" if theme_manager.current_theme() == theme_manager.LIGHT else "Nền tối"
            self.statusBar().showMessage(f"Giao diện: {current_theme}")
    
    def on_add_new_vehicle(self):
        """Show dialog to add new vehicle"""
        # Switch to registration tab
        self.tab_widget.setCurrentIndex(0)
        
        # Focus on first input field after a short delay
        QTimer.singleShot(100, lambda: self.owner_name_input.setFocus() if hasattr(self, 'owner_name_input') else None)
    
    def refresh_data(self):
        """Refresh all data views"""
        # Determine current tab and refresh accordingly
        current_tab = self.tab_widget.currentIndex()
        
        if current_tab == 1:  # List tab
            from ui.list_tab import refresh_vehicle_list
            refresh_vehicle_list(self)
        elif current_tab == 2:  # Search tab
            if hasattr(self, 'reset_search_tab'):
                self.reset_search_tab()