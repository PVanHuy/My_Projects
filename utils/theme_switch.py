# utils/theme_switch.py
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QRect, QPropertyAnimation, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush

from utils.theme_manager import theme_manager

class ThemeSwitch(QWidget):
    """Custom toggle switch widget for theme switching"""
    
    toggled = pyqtSignal(bool)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(60, 30)  # Fixed size for the switch
        
        # State
        self._is_checked = theme_manager.current_theme() == theme_manager.DARK
        
        # Animation
        self._handle_position = 30 if self._is_checked else 4
        self._animation = QPropertyAnimation(self, b"handle_position")
        self._animation.setDuration(200)
        
        # Colors
        self._track_color_on = QColor(52, 120, 246)   # Blue when ON (dark mode)
        self._track_color_off = QColor(230, 230, 230) # Light gray when OFF (light mode)
        self._handle_color = QColor(255, 255, 255)    # White handle
        
        # Set cursor
        self.setCursor(Qt.PointingHandCursor)
        
        # Set tooltip
        self.update_tooltip()
    
    def update_tooltip(self):
        if self._is_checked:
            self.setToolTip("Chuyển sang chế độ sáng")
        else:
            self.setToolTip("Chuyển sang chế độ tối")
    
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        
        # Calculate track and handle rects
        track_rect = QRect(0, 0, self.width(), self.height())
        handle_rect = QRect(self._handle_position, 4, 22, 22)
        
        # Draw track
        track_color = self._track_color_on if self._is_checked else self._track_color_off
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(track_color))
        p.drawRoundedRect(track_rect, 15, 15)
        
        # Draw handle
        p.setPen(QPen(QColor(180, 180, 180, 40)))
        p.setBrush(QBrush(self._handle_color))
        p.drawEllipse(handle_rect)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._is_checked = not self._is_checked
            self.update_tooltip()
            
            # Animate the handle
            start_pos = self._handle_position
            end_pos = 30 if self._is_checked else 4
            
            self._animation.setStartValue(start_pos)
            self._animation.setEndValue(end_pos)
            self._animation.start()
            
            # Emit signal
            self.toggled.emit(self._is_checked)
            
            # Toggle the theme
            theme_manager.toggle_theme()
            
            # Update the appearance
            self.update()
    
    def get_handle_position(self):
        return self._handle_position
    
    def set_handle_position(self, pos):
        self._handle_position = pos
        self.update()
    
    handle_position = property(get_handle_position, set_handle_position)