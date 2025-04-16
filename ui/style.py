from colors.my_colors import MyColor
from PyQt5.QtCore import QPropertyAnimation, QEasingCurve, QPoint, QSize
from PyQt5.QtWidgets import QGraphicsOpacityEffect, QLabel, QPushButton
from PyQt5.QtGui import QFont, QIcon
from utils.theme_manager import theme_manager

def apply_stylesheet(window):
    # Make sure colors are updated with current theme
    theme_manager.update_colors()
    
    # Get current theme name for specialized styling
    current_theme = theme_manager.current_theme()
    
    # Theme-specific additional styles
    if current_theme == theme_manager.DARK:
        additional_styles = f"""
            /* Dark mode specific overrides */
            QToolTip {{
                background-color: {MyColor.BLACK};
                color: {MyColor.TEXT_PRIMARY};
                border: 1px solid {MyColor.ACCENT};
            }}
            
            QStatusBar {{
                background-color: {MyColor.BLACK};
                color: {MyColor.TEXT_SECONDARY};
            }}
            
            QMenuBar {{
                background-color: {MyColor.BLACK};
                color: {MyColor.TEXT_PRIMARY};
            }}
            
            QMenuBar::item:selected {{
                background-color: {MyColor.SECONDARY};
            }}
            
            QMenu {{
                background-color: {MyColor.BLACK};
                color: {MyColor.TEXT_PRIMARY};
                border: 1px solid {MyColor.GRAY};
            }}
            
            QMenu::item:selected {{
                background-color: {MyColor.SECONDARY};
            }}
            
            QToolBar {{
                background-color: {MyColor.BLACK};
                border-bottom: 1px solid {MyColor.GRAY};
            }}
        """
    else:
        additional_styles = ""
    
    window.setStyleSheet(f"""
        /* Main application styles */
        QWidget {{
            font-family: 'Segoe UI', 'Arial', sans-serif;
            font-size: 14px;
            background-color: {MyColor.BACKGROUND};
        }}
        
        /* Tab Widget styles */
        QTabWidget::pane {{
            border: 1px solid {MyColor.GRAY};
            border-radius: 10px;
            background-color: {MyColor.WHITE};
            top: -1px;
            padding: 5px;
        }}
        
        QTabBar::tab {{
            background: {MyColor.SECONDARY};
            color: {MyColor.WHITE};
            padding: 12px 24px;
            border-top-left-radius: 12px;
            border-top-right-radius: 12px;
            margin-right: 4px;
            min-width: 100px;
            font-weight: bold;
        }}
        
        QTabBar::tab:selected {{
            background: {MyColor.PRIMARY};
            color: {MyColor.WHITE};
            border-bottom-color: {MyColor.PRIMARY};
        }}
        
        QTabBar::tab:hover {{
            background: {MyColor.ACCENT};
        }}
        
        /* Form elements */
        QLineEdit, QTextEdit, QComboBox {{
            border: 1px solid {MyColor.GRAY};
            border-radius: 8px;
            padding: 8px 12px;
            background-color: {MyColor.WHITE};
            selection-background-color: {MyColor.ACCENT};
            selection-color: {MyColor.WHITE};
            min-height: 20px;
        }}
        
        QLineEdit:focus, QTextEdit:focus, QComboBox:focus {{
            border: 2px solid {MyColor.ACCENT};
        }}
        
        QLineEdit:hover, QTextEdit:hover, QComboBox:hover {{
            border: 1px solid {MyColor.ACCENT};
        }}
        
        QLineEdit:disabled, QTextEdit:disabled, QComboBox:disabled {{
            background-color: {MyColor.LIGHT_GRAY};
            color: {MyColor.TEXT_SECONDARY};
        }}
        
        QComboBox {{
            padding-right: 20px;
        }}
        
        QComboBox::drop-down {{
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 20px;
            border-left-width: 0px;
            border-left-color: {MyColor.GRAY};
            border-left-style: solid;
            border-top-right-radius: 8px;
            border-bottom-right-radius: 8px;
        }}
        
        /* Button styles */
        QPushButton {{
            background-color: {MyColor.PRIMARY};
            color: {MyColor.WHITE};
            padding: 10px 20px;
            border-radius: 8px;
            font-weight: bold;
            min-height: 20px;
            border: none;
        }}
        
        QPushButton:hover {{
            background-color: {MyColor.PRIMARY_HOVER};
        }}
        
        QPushButton:pressed {{
            background-color: {MyColor.SECONDARY};
            padding-top: 11px;
            padding-bottom: 9px;
        }}
        
        QPushButton:disabled {{
            background-color: {MyColor.GRAY};
            color: {MyColor.TEXT_SECONDARY};
        }}

        /* Specialized buttons */
        QPushButton#exportButton, QPushButton#exportInfoButton {{
            background-color: {MyColor.SUCCESS};
            color: {MyColor.WHITE};
        }}
        QPushButton#exportButton:hover, QPushButton#exportInfoButton:hover {{
            background-color: {MyColor.SUCCESS_HOVER};
        }}

        QPushButton#deleteButton {{
            background-color: {MyColor.DANGER};
            color: {MyColor.WHITE};
        }}
        QPushButton#deleteButton:hover {{
            background-color: {MyColor.DANGER_HOVER};
        }}

        QPushButton#searchButton {{
            background-color: {MyColor.SECONDARY};
            color: {MyColor.WHITE};
        }}
        QPushButton#searchButton:hover {{
            background-color: {MyColor.SECONDARY_HOVER};
        }}

        QPushButton#clearButton, QPushButton#resetButton {{
            background-color: {MyColor.INFO};
            color: {MyColor.WHITE};
        }}
        QPushButton#clearButton:hover, QPushButton#resetButton:hover {{
            background-color: {MyColor.INFO_HOVER};
        }}
        
        /* Group box styles */
        QGroupBox {{
            border: 1px solid {MyColor.GRAY};
            border-radius: 8px;
            margin-top: 20px;
            padding-top: 25px;
            font-weight: bold;
            background-color: {MyColor.WHITE};
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top center;
            padding: 0 10px;
            color: {MyColor.PRIMARY};
            background-color: {MyColor.WHITE};
            font-size: 15px;
        }}
        
        /* Table styles */
        QTableWidget {{
            border: 1px solid {MyColor.GRAY};
            border-radius: 5px;
            gridline-color: {MyColor.LIGHT_GRAY};
            selection-background-color: {MyColor.ACCENT};
            selection-color: {MyColor.WHITE};
            alternate-background-color: {MyColor.LIGHT_GRAY};
        }}
        
        QTableWidget::item {{
            padding: 8px;
            border-bottom: 1px solid {MyColor.LIGHT_GRAY};
        }}
        
        QTableWidget::item:selected {{
            background-color: {MyColor.ACCENT};
            color: {MyColor.WHITE};
        }}
        
        QTableWidget::item:hover {{
            background-color: rgba(121, 215, 190, 0.2);
        }}
        
        QHeaderView::section {{
            background-color: {MyColor.PRIMARY};
            color: {MyColor.WHITE};
            padding: 10px;
            border: none;
            font-weight: bold;
            text-align: center;
        }}
        
        /* Scrollbar styles */
        QScrollBar:vertical {{
            border: none;
            background: {MyColor.LIGHT_GRAY};
            width: 12px;
            border-radius: 6px;
            margin: 14px 0px 14px 0px;
        }}
        
        QScrollBar::handle:vertical {{
            background: {MyColor.SECONDARY};
            border-radius: 6px;
            min-height: 20px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background: {MyColor.ACCENT};
        }}
        
        QScrollBar::add-line:vertical {{
            border: none;
            background: {MyColor.GRAY};
            height: 14px;
            border-bottom-left-radius: 6px;
            border-bottom-right-radius: 6px;
            subcontrol-position: bottom;
            subcontrol-origin: margin;
        }}
        
        QScrollBar::sub-line:vertical {{
            border: none;
            background: {MyColor.GRAY};
            height: 14px;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
            subcontrol-position: top;
            subcontrol-origin: margin;
        }}
        
        QScrollBar:horizontal {{
            border: none;
            background: {MyColor.LIGHT_GRAY};
            height: 12px;
            border-radius: 6px;
            margin: 0px 14px 0px 14px;
        }}
        
        QScrollBar::handle:horizontal {{
            background: {MyColor.SECONDARY};
            border-radius: 6px;
            min-width: 20px;
        }}
        
        QScrollBar::handle:horizontal:hover {{
            background: {MyColor.ACCENT};
        }}
        
        QScrollBar::add-line:horizontal {{
            border: none;
            background: {MyColor.GRAY};
            width: 14px;
            border-top-right-radius: 6px;
            border-bottom-right-radius: 6px;
            subcontrol-position: right;
            subcontrol-origin: margin;
        }}
        
        QScrollBar::sub-line:horizontal {{
            border: none;
            background: {MyColor.GRAY};
            width: 14px;
            border-top-left-radius: 6px;
            border-bottom-left-radius: 6px;
            subcontrol-position: left;
            subcontrol-origin: margin;
        }}
        
        /* Labels */
        QLabel {{
            color: {MyColor.TEXT_PRIMARY};
        }}
        
        QLabel#title {{
            font-size: 22px;
            font-weight: bold;
            color: {MyColor.PRIMARY};
        }}
        
        /* Message box */
        QMessageBox {{
            background-color: {MyColor.WHITE};
        }}
        
        QMessageBox QLabel {{
            color: {MyColor.TEXT_PRIMARY};
            min-width: 250px;
        }}
        
        QMessageBox QPushButton {{
            min-width: 100px;
        }}
    """)


def setup_animation(widget, animation_type="fade", duration=500):
    """Set up animations for widgets with configurable types and duration"""
    
    if animation_type == "fade":
        opacity_effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(opacity_effect)

        opacity_anim = QPropertyAnimation(opacity_effect, b"opacity")
        opacity_anim.setDuration(duration)
        opacity_anim.setStartValue(0)
        opacity_anim.setEndValue(1)
        opacity_anim.setEasingCurve(QEasingCurve.InOutQuad)
        opacity_anim.start()
        widget.animation = opacity_anim

    elif animation_type == "slide_right":
        pos_anim = QPropertyAnimation(widget, b"pos")
        start_pos = widget.pos()
        pos_anim.setDuration(duration)
        pos_anim.setStartValue(QPoint(start_pos.x() - 50, start_pos.y()))
        pos_anim.setEndValue(start_pos)
        pos_anim.setEasingCurve(QEasingCurve.OutCubic)
        pos_anim.start()
        widget.animation = pos_anim

    elif animation_type == "slide_left":
        pos_anim = QPropertyAnimation(widget, b"pos")
        start_pos = widget.pos()
        pos_anim.setDuration(duration)
        pos_anim.setStartValue(QPoint(start_pos.x() + 50, start_pos.y()))
        pos_anim.setEndValue(start_pos)
        pos_anim.setEasingCurve(QEasingCurve.OutCubic)
        pos_anim.start()
        widget.animation = pos_anim

    elif animation_type == "slide_up":
        pos_anim = QPropertyAnimation(widget, b"pos")
        start_pos = widget.pos()
        pos_anim.setDuration(duration)
        pos_anim.setStartValue(QPoint(start_pos.x(), start_pos.y() + 50))
        pos_anim.setEndValue(start_pos)
        pos_anim.setEasingCurve(QEasingCurve.OutCubic)
        pos_anim.start()
        widget.animation = pos_anim
        
    elif animation_type == "slide_down":
        pos_anim = QPropertyAnimation(widget, b"pos")
        start_pos = widget.pos()
        pos_anim.setDuration(duration)
        pos_anim.setStartValue(QPoint(start_pos.x(), start_pos.y() - 50))
        pos_anim.setEndValue(start_pos)
        pos_anim.setEasingCurve(QEasingCurve.OutCubic)
        pos_anim.start()
        widget.animation = pos_anim
        
    elif animation_type == "zoom_in":
        # Store original size for later
        widget._original_size = widget.size()
        
        # Start with a small size
        widget.resize(int(widget.width() * 0.8), int(widget.height() * 0.8))
        
        # Create size animation
        size_anim = QPropertyAnimation(widget, b"size")
        size_anim.setDuration(duration)
        size_anim.setStartValue(widget.size())
        size_anim.setEndValue(widget._original_size)
        size_anim.setEasingCurve(QEasingCurve.OutBack)
        size_anim.start()
        widget.animation = size_anim


def create_title_label(text, icon_name=None, icon_color=MyColor.PRIMARY):
    """Create a standardized title label with an optional icon"""
    from PyQt5.QtWidgets import QHBoxLayout, QWidget
    from utils.app_icons import AppIcons
    
    container = QWidget()
    layout = QHBoxLayout(container)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(15)
    
    if icon_name:
        icon_label = QLabel()
        icon_label.setPixmap(AppIcons.get_pixmap(icon_name, icon_color, QSize(48, 48)))
        layout.addWidget(icon_label)
    
    title = QLabel(text)
    title.setFont(QFont("Arial", 22, QFont.Bold))
    title.setStyleSheet(f"color: {MyColor.PRIMARY};")
    title.setObjectName("title")
    
    layout.addWidget(title)
    layout.addStretch()
    
    return container


def create_styled_button(text, icon_name=None, button_type="default", height=40, width=None):
    """Create a standardized button with proper styling and icon"""
    from utils.app_icons import AppIcons
    
    button = QPushButton(text)
    
    if button_type == "primary":
        button.setObjectName("primaryButton")
    elif button_type == "secondary":
        button.setObjectName("searchButton")  # Reuse existing style
    elif button_type == "danger":
        button.setObjectName("deleteButton")
    elif button_type == "success":
        button.setObjectName("exportButton") 
    elif button_type == "info":
        button.setObjectName("clearButton")
    else:
        button.setObjectName("defaultButton")
    
    if icon_name:
        button.setIcon(AppIcons.get_icon(icon_name))
    
    button.setMinimumHeight(height)
    if width:
        button.setMinimumWidth(width)
    
    return button