from PyQt5.QtCore import QObject, pyqtSignal, QSettings
from colors.my_colors import MyColor

class ThemeManager(QObject):
    """
    Lớp quản lý chủ đề ứng dụng (chế độ sáng/tối)
    """
    themeChanged = pyqtSignal(str)  # Tín hiệu được phát ra khi chủ đề thay đổi
    
    # Các loại chủ đề
    LIGHT = "light"
    DARK = "dark"
    
    def __init__(self):
        super().__init__()
        self.settings = QSettings("VehicleRegistrationApp", "Settings")
        self._current_theme = self.settings.value("theme", self.LIGHT)
        self._init_colors()
    
    def _init_colors(self):
        """Khởi tạo bảng màu cho cả hai chủ đề"""
        # Chủ đề sáng (màu mặc định)
        self.light_colors = {
            # Màu chính
            "PRIMARY": "#2E5077",
            "SECONDARY": "#4DA1A9",
            "ACCENT": "#79D7BE",
            
            # Màu nền
            "BACKGROUND": "#F6F4F0",
            "WHITE": "#FFFFFF",
            "BLACK": "#000000",
            "GRAY": "#CCCCCC",
            "LIGHT_GRAY": "#E6E6E6",
            
            # Màu trạng thái
            "SUCCESS": "#28a745",
            "WARNING": "#ffc107",
            "DANGER": "#dc3545",
            "INFO": "#17a2b8",
            "OBJECT": "#92b9E3",
            
            # Màu khi di chuột qua
            "PRIMARY_HOVER": "#254366",
            "SECONDARY_HOVER": "#3d8a91",
            "ACCENT_HOVER": "#66c2a9",
            "SUCCESS_HOVER": "#22913c",
            "WARNING_HOVER": "#e5ac06",
            "DANGER_HOVER": "#c82333",
            "INFO_HOVER": "#138496",
            
            # Màu văn bản
            "TEXT_PRIMARY": "#212529",
            "TEXT_SECONDARY": "#6c757d",
            "TEXT_LIGHT": "#f8f9fa"
        }
        
        # Chủ đề tối
        self.dark_colors = {
            # Màu chính
            "PRIMARY": "#4DA1A9",        # Đổi vị trí màu chính và phụ trong chế độ tối
            "SECONDARY": "#2E5077",
            "ACCENT": "#79D7BE",
            
            # Màu nền
            "BACKGROUND": "#1E1E1E",
            "WHITE": "#2D2D30",          # Nền panel tối
            "BLACK": "#000000",
            "GRAY": "#3E3E42",
            "LIGHT_GRAY": "#333337",
            
            # Màu trạng thái (hơi dịu cho chủ đề tối)
            "SUCCESS": "#2EBD59",
            "WARNING": "#FFC440",
            "DANGER": "#E74C3C",
            "INFO": "#25A4CF",
            "OBJECT": "#7DA7D9",
            
            # Màu khi di chuột qua
            "PRIMARY_HOVER": "#3d8a91",
            "SECONDARY_HOVER": "#254366",
            "ACCENT_HOVER": "#66c2a9",
            "SUCCESS_HOVER": "#27A745",
            "WARNING_HOVER": "#E5AC06",
            "DANGER_HOVER": "#C82333",
            "INFO_HOVER": "#138496",
            
            # Màu văn bản
            "TEXT_PRIMARY": "#F0F0F0",
            "TEXT_SECONDARY": "#BCBCBC",
            "TEXT_LIGHT": "#FFFFFF"
        }
    
    def current_theme(self):
        """Lấy tên chủ đề hiện tại"""
        return self._current_theme
    
    def set_theme(self, theme_name):
        """Thiết lập chủ đề hiện tại và lưu vào cài đặt"""
        if theme_name in [self.LIGHT, self.DARK]:
            old_theme = self._current_theme
            self._current_theme = theme_name
            self.settings.setValue("theme", theme_name)
            
            # Chỉ phát tín hiệu nếu chủ đề thực sự thay đổi
            if old_theme != theme_name:
                self.update_colors()
                self.themeChanged.emit(theme_name)
    
    def toggle_theme(self):
        """Chuyển đổi giữa chủ đề sáng và tối"""
        if self._current_theme == self.LIGHT:
            self.set_theme(self.DARK)
        else:
            self.set_theme(self.LIGHT)
    
    def update_colors(self):
        """Cập nhật lớp MyColor với màu sắc của chủ đề hiện tại"""
        colors = self.light_colors if self._current_theme == self.LIGHT else self.dark_colors
        
        # Cập nhật các thuộc tính của lớp MyColor một cách động
        for color_name, color_value in colors.items():
            if hasattr(MyColor, color_name):
                setattr(MyColor, color_name, color_value)
    
    def get_current_colors(self):
        """Lấy bảng màu của chủ đề hiện tại"""
        return self.light_colors if self._current_theme == self.LIGHT else self.dark_colors

# Tạo một thể hiện toàn cục của ThemeManager
theme_manager = ThemeManager()