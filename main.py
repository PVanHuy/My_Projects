import sys
from PyQt5.QtWidgets import QApplication
from app import LicensePlateApp
from database.db_manager import DatabaseManager

def main():
    # Khởi tạo database và nhập dữ liệu mẫu nếu cần
    db = DatabaseManager()
    db.import_sample_data()  # Chỉ nhập dữ liệu nếu database trống
    
    app = QApplication(sys.argv)
    window = LicensePlateApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()