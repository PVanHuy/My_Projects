import qtawesome as qta
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QIcon, QPixmap, QColor, QPainter
from colors.my_colors import MyColor
import logging

class AppIcons:
    """Class that manages application icons using QtAwesome"""
    
    @staticmethod
    def get_icon(icon_name, color=MyColor.PRIMARY, size=None):
        """Get a QtAwesome icon with specified parameters"""
        if icon_name is None:
            # Return empty icon if None is provided
            return QIcon()
            
        options = {'color': color}
        if size:
            options['scale_factor'] = size / 16  # Assuming 16px as base size
        
        # Map icon names to FontAwesome names
        icon_map = {
            # Tab icons
            'register': 'fa5s.car',
            'list': 'fa5s.list-alt',
            'search': 'fa5s.search',
            'stats': 'fa5s.chart-bar',
            
            # Action icons
            'save': 'fa5s.save',
            'delete': 'fa5s.trash-alt',
            'export': 'fa5s.file-export',
            'import': 'fa5s.file-import',
            'refresh': 'fa5s.sync-alt',
            'add': 'fa5s.plus-circle',
            'edit': 'fa5s.edit',
            'upload': 'fa5s.upload',
            'download': 'fa5s.download',
            'detect': 'fa5s.camera',
            'print': 'fa5s.print',
            'filter': 'fa5s.filter',
            'settings': 'fa5s.cog',
            'info': 'fa5s.info-circle',
            'warning': 'fa5s.exclamation-triangle',
            'success': 'fa5s.check-circle',
            'error': 'fa5s.times-circle',
            'user': 'fa5s.user',
            'calendar': 'fa5s.calendar-alt',
            'help': 'fa5s.question-circle',
            'login': 'fa5s.sign-in-alt',
            'logout': 'fa5s.sign-out-alt',
            'home': 'fa5s.home',
            'clock': 'fa5s.clock',
            'email': 'fa5s.envelope',
            'phone': 'fa5s.phone',
            'location': 'fa5s.map-marker-alt',
            'car': 'fa5s.car',
            'motorcycle': 'fa5s.motorcycle',
            'truck': 'fa5s.truck',
            'bus': 'fa5s.bus',
            'app': 'fa5s.id-card',
            'cancel': 'fa5s.times',
            
            # Theme related icons
            'moon': 'fa5s.moon',
            'sun': 'fa5s.sun',
            'palette': 'fa5s.palette',
            
            # Menu and toolbar icons
            'file': 'fa5s.file',
            'folder': 'fa5s.folder',
            'folder-open': 'fa5s.folder-open',
            'file-csv': 'fa5s.file-csv',
            'file-excel': 'fa5s.file-excel',
            'file-pdf': 'fa5s.file-pdf',
            'file-image': 'fa5s.file-image',
            'file-code': 'fa5s.file-code',
            'camera-alt': 'fa5s.camera',
            'camera': 'fa5s.camera', 
            'database': 'fa5s.database',
            'server': 'fa5s.server',
            'cloud': 'fa5s.cloud',
            'cloud-upload': 'fa5s.cloud-upload-alt',
            'cloud-download': 'fa5s.cloud-download-alt'
        }
        
        try:
            # Attempt to use the mapped icon name or the provided name if not in map
            fa_name = icon_map.get(icon_name.lower(), icon_name)
            return qta.icon(fa_name, **options)
        except Exception as e:
            # Log error and create a fallback icon
            logging.warning(f"Error creating icon '{icon_name}': {str(e)}")
            
            # Create a simple fallback icon
            return AppIcons._create_fallback_icon(color)
    
    @staticmethod
    def _create_fallback_icon(color=MyColor.PRIMARY):
        """Create a simple fallback icon when QtAwesome fails"""
        icon = QIcon()
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.transparent)
        
        # Draw a simple shape as fallback
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(color))
        painter.drawRect(16, 16, 32, 32)
        painter.end()
        
        icon.addPixmap(pixmap)
        return icon
    
    @staticmethod
    def get_pixmap(icon_name, color=MyColor.PRIMARY, size=QSize(32, 32)):
        """Convert a QtAwesome icon to QPixmap with specified size"""
        if isinstance(size, int):
            size = QSize(size, size)
        
        icon = AppIcons.get_icon(icon_name, color)
        return icon.pixmap(size)
    
    @staticmethod
    def create_colored_button_icon(icon_name, normal_color=MyColor.PRIMARY, hover_color=MyColor.ACCENT):
        """Create an icon with normal and hover states for buttons"""
        try:
            normal_icon = AppIcons.get_icon(icon_name, normal_color)
            hover_icon = AppIcons.get_icon(icon_name, hover_color)
            
            icon = QIcon()
            icon.addPixmap(normal_icon.pixmap(32), QIcon.Normal, QIcon.Off)
            icon.addPixmap(hover_icon.pixmap(32), QIcon.Active, QIcon.Off)
            icon.addPixmap(hover_icon.pixmap(32), QIcon.Selected, QIcon.Off)
            icon.addPixmap(hover_icon.pixmap(32), QIcon.Selected, QIcon.On)
            
            return icon
        except Exception as e:
            logging.warning(f"Error creating colored button icon: {str(e)}")
            return AppIcons.get_icon(icon_name, normal_color)