import qtawesome as qta
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QIcon, QPixmap, QColor, QPainter
from colors.my_colors import MyColor
import logging

class AppIcons:
    """Lớp quản lý các biểu tượng ứng dụng sử dụng QtAwesome"""
    
    @staticmethod
    def get_icon(icon_name, color=MyColor.PRIMARY, size=None):
        """Lấy biểu tượng QtAwesome với các thông số chỉ định"""
        if icon_name is None:
            # Trả về biểu tượng rỗng nếu không có tên
            return QIcon()
            
        options = {'color': color}
        if size:
            options['scale_factor'] = size / 16  # Giả định kích thước cơ sở là 16px
        
        # Ánh xạ tên biểu tượng tới tên FontAwesome
        icon_map = {
            # Biểu tượng tab
            'register': 'fa5s.car',
            'list': 'fa5s.list-alt',
            'search': 'fa5s.search',
            'stats': 'fa5s.chart-bar',
            
            # Biểu tượng hành động
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
            
            # Biểu tượng liên quan đến giao diện
            'moon': 'fa5s.moon',
            'sun': 'fa5s.sun',
            'palette': 'fa5s.palette',
            
            # Biểu tượng menu và thanh công cụ
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
            'history': 'fa5s.history',
            'cloud-download': 'fa5s.cloud-download-alt'
        }
        
        try:
            # Sử dụng tên biểu tượng đã ánh xạ hoặc tên đã cung cấp nếu không có trong bản đồ
            fa_name = icon_map.get(icon_name.lower(), icon_name)
            return qta.icon(fa_name, **options)
        except Exception as e:
            # Ghi lại lỗi và tạo biểu tượng dự phòng
            logging.warning(f"Lỗi khi tạo biểu tượng '{icon_name}': {str(e)}")
            
            # Tạo biểu tượng dự phòng đơn giản
            return AppIcons._create_fallback_icon(color)
    
    @staticmethod
    def _create_fallback_icon(color=MyColor.PRIMARY):
        """Tạo biểu tượng dự phòng đơn giản khi QtAwesome thất bại"""
        icon = QIcon()
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.transparent)
        
        # Vẽ hình dạng đơn giản làm biểu tượng dự phòng
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
        """Chuyển đổi biểu tượng QtAwesome thành QPixmap với kích thước chỉ định"""
        if isinstance(size, int):
            size = QSize(size, size)
        
        icon = AppIcons.get_icon(icon_name, color)
        return icon.pixmap(size)
    
    @staticmethod
    def create_colored_button_icon(icon_name, normal_color=MyColor.PRIMARY, hover_color=MyColor.ACCENT):
        """Tạo biểu tượng với trạng thái bình thường và di chuột cho các nút"""
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
            logging.warning(f"Lỗi khi tạo biểu tượng nút màu: {str(e)}")
            return AppIcons.get_icon(icon_name, normal_color)