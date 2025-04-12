from PyQt5.QtCore import QObject, pyqtSignal, QSettings
from colors.my_colors import MyColor

class ThemeManager(QObject):
    """
    Class to manage the application theme (light/dark mode)
    """
    themeChanged = pyqtSignal(str)  # Signal emitted when theme changes
    
    # Theme types
    LIGHT = "light"
    DARK = "dark"
    
    def __init__(self):
        super().__init__()
        self.settings = QSettings("VehicleRegistrationApp", "Settings")
        self._current_theme = self.settings.value("theme", self.LIGHT)
        self._init_colors()
    
    def _init_colors(self):
        """Initialize color schemes for both themes"""
        # Light theme (default colors)
        self.light_colors = {
            # Main colors
            "PRIMARY": "#2E5077",
            "SECONDARY": "#4DA1A9",
            "ACCENT": "#79D7BE",
            
            # Background colors
            "BACKGROUND": "#F6F4F0",
            "WHITE": "#FFFFFF",
            "BLACK": "#000000",
            "GRAY": "#CCCCCC",
            "LIGHT_GRAY": "#E6E6E6",
            
            # Status colors
            "SUCCESS": "#28a745",
            "WARNING": "#ffc107",
            "DANGER": "#dc3545",
            "INFO": "#17a2b8",
            "OBJECT": "#92b9E3",
            
            # Hover colors
            "PRIMARY_HOVER": "#254366",
            "SECONDARY_HOVER": "#3d8a91",
            "ACCENT_HOVER": "#66c2a9",
            "SUCCESS_HOVER": "#22913c",
            "WARNING_HOVER": "#e5ac06",
            "DANGER_HOVER": "#c82333",
            "INFO_HOVER": "#138496",
            
            # Text colors
            "TEXT_PRIMARY": "#212529",
            "TEXT_SECONDARY": "#6c757d",
            "TEXT_LIGHT": "#f8f9fa"
        }
        
        # Dark theme
        self.dark_colors = {
            # Main colors
            "PRIMARY": "#4DA1A9",        # Swap primary and secondary for dark mode
            "SECONDARY": "#2E5077",
            "ACCENT": "#79D7BE",
            
            # Background colors
            "BACKGROUND": "#1E1E1E",
            "WHITE": "#2D2D30",          # Dark panel background
            "BLACK": "#000000",
            "GRAY": "#3E3E42",
            "LIGHT_GRAY": "#333337",
            
            # Status colors (slightly muted for dark theme)
            "SUCCESS": "#2EBD59",
            "WARNING": "#FFC440",
            "DANGER": "#E74C3C",
            "INFO": "#25A4CF",
            "OBJECT": "#7DA7D9",
            
            # Hover colors
            "PRIMARY_HOVER": "#3d8a91",
            "SECONDARY_HOVER": "#254366",
            "ACCENT_HOVER": "#66c2a9",
            "SUCCESS_HOVER": "#27A745",
            "WARNING_HOVER": "#E5AC06",
            "DANGER_HOVER": "#C82333",
            "INFO_HOVER": "#138496",
            
            # Text colors
            "TEXT_PRIMARY": "#F0F0F0",
            "TEXT_SECONDARY": "#BCBCBC",
            "TEXT_LIGHT": "#FFFFFF"
        }
    
    def current_theme(self):
        """Get the current theme name"""
        return self._current_theme
    
    def set_theme(self, theme_name):
        """Set the current theme and save to settings"""
        if theme_name in [self.LIGHT, self.DARK]:
            old_theme = self._current_theme
            self._current_theme = theme_name
            self.settings.setValue("theme", theme_name)
            
            # Only emit signal if theme actually changed
            if old_theme != theme_name:
                self.update_colors()
                self.themeChanged.emit(theme_name)
    
    def toggle_theme(self):
        """Toggle between light and dark themes"""
        if self._current_theme == self.LIGHT:
            self.set_theme(self.DARK)
        else:
            self.set_theme(self.LIGHT)
    
    def update_colors(self):
        """Update MyColor class with current theme colors"""
        colors = self.light_colors if self._current_theme == self.LIGHT else self.dark_colors
        
        # Update the MyColor class attributes dynamically
        for color_name, color_value in colors.items():
            if hasattr(MyColor, color_name):
                setattr(MyColor, color_name, color_value)
    
    def get_current_colors(self):
        """Get the current theme's colors"""
        return self.light_colors if self._current_theme == self.LIGHT else self.dark_colors

# Create a global instance of ThemeManager
theme_manager = ThemeManager()