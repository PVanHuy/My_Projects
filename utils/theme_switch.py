from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QRect, QPropertyAnimation, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush

from utils.theme_manager import theme_manager

class ThemeSwitch(QWidget):
    """Widget công tắc tùy chỉnh để chuyển đổi chủ đề"""
    
    toggled = pyqtSignal(bool)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(60, 30)  # Kích thước cố định cho công tắc
        
        # Trạng thái
        self._is_checked = theme_manager.current_theme() == theme_manager.DARK
        
        # Hiệu ứng chuyển động
        self._handle_position = 30 if self._is_checked else 4
        self._animation = QPropertyAnimation(self, b"handle_position")
        self._animation.setDuration(200)
        
        # Màu sắc
        self._track_color_on = QColor(52, 120, 246)   # Màu xanh khi BẬT (chế độ tối)
        self._track_color_off = QColor(230, 230, 230) # Màu xám nhạt khi TẮT (chế độ sáng)
        self._handle_color = QColor(255, 255, 255)    # Núm trắng
        
        # Thiết lập con trỏ
        self.setCursor(Qt.PointingHandCursor)
        
        # Thiết lập tooltip
        self.update_tooltip()
    
    def update_tooltip(self):
        """Cập nhật gợi ý khi di chuột qua"""
        if self._is_checked:
            self.setToolTip("Chuyển sang chế độ sáng")
        else:
            self.setToolTip("Chuyển sang chế độ tối")
    
    def paintEvent(self, event):
        """Vẽ công tắc chuyển đổi chủ đề"""
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        
        # Tính toán hình chữ nhật cho đường ray và núm
        track_rect = QRect(0, 0, self.width(), self.height())
        handle_rect = QRect(self._handle_position, 4, 22, 22)
        
        # Vẽ đường ray
        track_color = self._track_color_on if self._is_checked else self._track_color_off
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(track_color))
        p.drawRoundedRect(track_rect, 15, 15)
        
        # Vẽ núm
        p.setPen(QPen(QColor(180, 180, 180, 40)))
        p.setBrush(QBrush(self._handle_color))
        p.drawEllipse(handle_rect)
    
    def mousePressEvent(self, event):
        """Xử lý sự kiện nhấp chuột"""
        if event.button() == Qt.LeftButton:
            self._is_checked = not self._is_checked
            self.update_tooltip()
            
            # Tạo hiệu ứng di chuyển núm
            start_pos = self._handle_position
            end_pos = 30 if self._is_checked else 4
            
            self._animation.setStartValue(start_pos)
            self._animation.setEndValue(end_pos)
            self._animation.start()
            
            # Phát tín hiệu
            self.toggled.emit(self._is_checked)
            
            # Chuyển đổi chủ đề
            theme_manager.toggle_theme()
            
            # Cập nhật giao diện
            self.update()
    
    def get_handle_position(self):
        """Lấy vị trí của núm công tắc"""
        return self._handle_position
    
    def set_handle_position(self, pos):
        """Thiết lập vị trí của núm công tắc"""
        self._handle_position = pos
        self.update()
    
    handle_position = property(get_handle_position, set_handle_position)