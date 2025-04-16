import sqlite3
import os
import traceback
import logging
from datetime import datetime

# Cấu hình logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DatabaseManager:
    def __init__(self, db_path="database/vehicle_registry.db"):
        self.db_path = db_path
        self.initialize_db()
    
    def initialize_db(self):
        """Tạo database và các bảng nếu chưa tồn tại"""
        # Đảm bảo thư mục tồn tại
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Cấu hình để bật tính năng foreign key constraints
            conn.execute("PRAGMA foreign_keys = ON")
            
            cursor = conn.cursor()
            
            # Tạo bảng Vehicle
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS vehicles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plate TEXT UNIQUE NOT NULL,
                owner TEXT NOT NULL,
                phone TEXT NOT NULL,
                vehicle_type TEXT NOT NULL,
                brand TEXT NOT NULL,
                color TEXT,
                register_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notes TEXT
            )
            ''')
            
            # Tạo bảng Images để lưu ảnh biển số
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS plate_images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vehicle_id INTEGER NOT NULL,
                image_path TEXT NOT NULL,
                upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (vehicle_id) REFERENCES vehicles (id) ON DELETE CASCADE
            )
            ''')
            
            # Tạo bảng History để lưu lịch sử thay đổi
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS change_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vehicle_id INTEGER NOT NULL,
                change_type TEXT NOT NULL,
                change_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                description TEXT,
                FOREIGN KEY (vehicle_id) REFERENCES vehicles (id) ON DELETE CASCADE
            )
            ''')
            
            # Tạo bảng settings để lưu cài đặt hệ thống
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS app_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                setting_key TEXT UNIQUE NOT NULL,
                setting_value TEXT,
                setting_type TEXT NOT NULL,
                update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # Tạo index cho tìm kiếm nhanh
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_vehicles_plate ON vehicles (plate)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_vehicles_owner ON vehicles (owner)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_vehicles_phone ON vehicles (phone)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_settings_key ON app_settings (setting_key)')
            
            conn.commit()
            
            # Thêm cài đặt mặc định nếu chưa có
            self.init_default_settings(cursor)
            
            conn.commit()
        except Exception as e:
            logging.error(f"Database initialization error: {e}")
            traceback.print_exc()
            if conn:
                conn.rollback()
        finally:
            if conn:
                conn.close()
    
    def init_default_settings(self, cursor):
        """Khởi tạo các cài đặt mặc định cho ứng dụng"""
        default_settings = [
            ('theme', 'light', 'string'),
            ('auto_recognize', 'true', 'boolean'),
            ('export_folder', os.path.expanduser('~/Documents'), 'string'),
            ('backup_interval', '7', 'integer')  # Số ngày giữa các lần backup tự động
        ]
        
        for key, value, type_name in default_settings:
            cursor.execute('''
            INSERT OR IGNORE INTO app_settings (setting_key, setting_value, setting_type)
            VALUES (?, ?, ?)
            ''', (key, value, type_name))
    
    def add_vehicle(self, plate, owner, phone, vehicle_type, brand, color="Không có thông tin", notes=""):
        """Thêm xe mới vào database"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute("PRAGMA foreign_keys = ON")
            cursor = conn.cursor()
            
            # Chuẩn hóa biển số (chuyển về chữ hoa)
            plate = plate.upper()
            
            # Kiểm tra xem biển số đã tồn tại chưa
            cursor.execute("SELECT id FROM vehicles WHERE plate = ?", (plate,))
            if cursor.fetchone():
                conn.close()
                return False, "Biển số đã tồn tại trong hệ thống"
            
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Thêm xe mới
            cursor.execute('''
            INSERT INTO vehicles (plate, owner, phone, vehicle_type, brand, color, register_time, last_update, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (plate, owner, phone, vehicle_type, brand, color, current_time, current_time, notes))
            
            vehicle_id = cursor.lastrowid
            
            # Thêm vào lịch sử
            cursor.execute('''
            INSERT INTO change_history (vehicle_id, change_type, description)
            VALUES (?, ?, ?)
            ''', (vehicle_id, "ADD", f"Thêm xe mới: {plate}"))
            
            conn.commit()
            
            # Tạo đối tượng vehicle để trả về
            new_vehicle = {
                "id": vehicle_id,
                "plate": plate,
                "owner": owner,
                "phone": phone,
                "type": vehicle_type,
                "brand": brand,
                "color": color,
                "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "notes": notes
            }
            
            return True, new_vehicle
            
        except Exception as e:
            logging.error(f"Error adding vehicle: {e}")
            traceback.print_exc()
            if conn:
                conn.rollback()
            return False, str(e)
        finally:
            if conn:
                conn.close()
    
    def update_vehicle(self, plate, **updates):
        """Cập nhật thông tin xe"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute("PRAGMA foreign_keys = ON")
            cursor = conn.cursor()
            
            # Chuẩn hóa biển số (chuyển về chữ hoa)
            plate = plate.upper()
            
            # Kiểm tra xem xe có tồn tại không
            cursor.execute("SELECT id FROM vehicles WHERE plate = ?", (plate,))
            result = cursor.fetchone()
            if not result:
                return False, "Không tìm thấy xe với biển số này"
                
            vehicle_id = result[0]
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Lấy thông tin hiện tại để ghi lịch sử thay đổi
            cursor.execute("SELECT * FROM vehicles WHERE id = ?", (vehicle_id,))
            current_data = cursor.fetchone()
            column_names = [desc[0] for desc in cursor.description]
            current_vehicle = dict(zip(column_names, current_data))
            
            # Chuẩn bị câu lệnh SQL và tham số
            allowed_fields = {'owner': 'owner', 'phone': 'phone', 'vehicle_type': 'type',
                             'brand': 'brand', 'color': 'color', 'notes': 'notes'}
            sql_fields = []
            sql_values = []
            changes = []
            
            for key, value in updates.items():
                db_field = allowed_fields.get(key)
                if db_field and value != current_vehicle.get(key):
                    sql_fields.append(f"{key} = ?")
                    sql_values.append(value)
                    changes.append(f"{key}: '{current_vehicle.get(key, '')}' -> '{value}'")
            
            # Nếu không có thay đổi
            if not changes:
                return True, "Không có thông tin nào thay đổi"
            
            # Thêm thời gian cập nhật
            sql_fields.append("last_update = ?")
            sql_values.append(current_time)
            
            # Thêm id để WHERE clause
            sql_values.append(vehicle_id)
            
            # Cập nhật thông tin xe
            sql_query = f"UPDATE vehicles SET {', '.join(sql_fields)} WHERE id = ?"
            cursor.execute(sql_query, sql_values)
            
            # Thêm vào lịch sử
            change_desc = f"Cập nhật thông tin xe {plate}: " + ", ".join(changes)
            cursor.execute('''
            INSERT INTO change_history (vehicle_id, change_type, description)
            VALUES (?, ?, ?)
            ''', (vehicle_id, "UPDATE", change_desc))
            
            conn.commit()
            
            # Lấy thông tin xe sau khi cập nhật
            cursor.execute("SELECT * FROM vehicles WHERE id = ?", (vehicle_id,))
            row = cursor.fetchone()
            column_names = [desc[0] for desc in cursor.description]
            updated_vehicle = dict(zip(column_names, row))
            
            # Chuyển đổi key cho tương thích với code hiện tại
            updated_vehicle['type'] = updated_vehicle.pop('vehicle_type')
            updated_vehicle['timestamp'] = datetime.strptime(
                updated_vehicle.pop('register_time'), "%Y-%m-%d %H:%M:%S"
            ).strftime("%d/%m/%Y %H:%M")
            
            return True, updated_vehicle
            
        except Exception as e:
            logging.error(f"Error updating vehicle: {e}")
            traceback.print_exc()
            if conn:
                conn.rollback()
            return False, str(e)
        finally:
            if conn:
                conn.close()
    
    def delete_vehicle(self, plate):
        """Xóa xe khỏi database"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute("PRAGMA foreign_keys = ON")
            cursor = conn.cursor()
            
            # Chuẩn hóa biển số
            plate = plate.upper()
            
            # Kiểm tra xem xe có tồn tại không
            cursor.execute("SELECT id, owner FROM vehicles WHERE plate = ?", (plate,))
            result = cursor.fetchone()
            if not result:
                return False, "Không tìm thấy xe với biển số này"
                
            vehicle_id, owner = result
            
            # Lưu lịch sử trước khi xóa
            cursor.execute('''
            INSERT INTO change_history (vehicle_id, change_type, description)
            VALUES (?, ?, ?)
            ''', (vehicle_id, "DELETE", f"Xóa xe biển số {plate} của chủ xe {owner}"))
            
            # Xóa các ảnh biển số (chỉ xóa record, không xóa file thật)
            cursor.execute("DELETE FROM plate_images WHERE vehicle_id = ?", (vehicle_id,))
            
            # Xóa xe
            cursor.execute("DELETE FROM vehicles WHERE id = ?", (vehicle_id,))
            
            conn.commit()
            
            return True, "Xóa xe thành công"
            
        except Exception as e:
            logging.error(f"Error deleting vehicle: {e}")
            traceback.print_exc()
            if conn:
                conn.rollback()
            return False, str(e)
        finally:
            if conn:
                conn.close()
    
    def search_vehicles(self, search_text=None, vehicle_type=None, brand=None, date=None, limit=100):
        """Tìm kiếm xe với nhiều tiêu chí"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            sql_query = "SELECT * FROM vehicles WHERE 1=1"
            sql_params = []
            
            if search_text:
                sql_query += " AND (plate LIKE ? OR owner LIKE ? OR phone LIKE ? OR notes LIKE ?)"
                search_pattern = f"%{search_text}%"
                sql_params.extend([search_pattern, search_pattern, search_pattern, search_pattern])
            
            if vehicle_type and vehicle_type != "Tất cả":
                sql_query += " AND vehicle_type = ?"
                sql_params.append(vehicle_type)
            
            if brand and brand != "Tất cả":
                sql_query += " AND brand = ?"
                sql_params.append(brand)
            
            if date:
                sql_query += " AND DATE(register_time) = DATE(?)"
                sql_params.append(date)
            
            sql_query += " ORDER BY register_time DESC LIMIT ?"
            sql_params.append(limit)
            
            cursor.execute(sql_query, sql_params)
            
            # Lấy tên cột
            column_names = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            
            # Chuyển đổi dữ liệu thành định dạng tương thích với code hiện tại
            results = []
            for row in rows:
                vehicle = dict(zip(column_names, row))
                
                # Chuyển đổi key names để tương thích với code hiện tại
                vehicle['type'] = vehicle.pop('vehicle_type')
                vehicle['timestamp'] = datetime.strptime(
                    vehicle.pop('register_time'), "%Y-%m-%d %H:%M:%S"
                ).strftime("%d/%m/%Y %H:%M")
                
                results.append(vehicle)
            
            return results
            
        except Exception as e:
            logging.error(f"Search error: {str(e)}")
            traceback.print_exc()
            return []
        finally:
            if conn:
                conn.close()
    
    def get_vehicle_by_plate(self, plate):
        """Lấy thông tin xe theo biển số"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Chuẩn hóa biển số
            plate = plate.upper()
            
            cursor.execute("SELECT * FROM vehicles WHERE plate = ?", (plate,))
            row = cursor.fetchone()
            
            if row:
                column_names = [desc[0] for desc in cursor.description]
                vehicle = dict(zip(column_names, row))
                
                # Chuyển đổi key cho tương thích với code hiện tại
                vehicle['type'] = vehicle.pop('vehicle_type')
                vehicle['timestamp'] = datetime.strptime(
                    vehicle.pop('register_time'), "%Y-%m-%d %H:%M:%S"
                ).strftime("%d/%m/%Y %H:%M")
                
                # Lấy ảnh biển số
                cursor.execute("""
                SELECT image_path FROM plate_images 
                WHERE vehicle_id = ? 
                ORDER BY upload_time DESC LIMIT 1
                """, (vehicle['id'],))
                
                image_result = cursor.fetchone()
                if image_result:
                    vehicle['image_path'] = image_result[0]
                else:
                    vehicle['image_path'] = None
                
                return vehicle
            else:
                return None
                
        except Exception as e:
            logging.error(f"Error getting vehicle: {str(e)}")
            traceback.print_exc()
            return None
        finally:
            if conn:
                conn.close()
    
    def add_plate_image(self, plate, image_path):
        """Thêm ảnh biển số cho xe"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute("PRAGMA foreign_keys = ON")
            cursor = conn.cursor()
            
            # Chuẩn hóa biển số
            plate = plate.upper()
            
            # Lấy vehicle_id từ biển số
            cursor.execute("SELECT id FROM vehicles WHERE plate = ?", (plate,))
            result = cursor.fetchone()
            
            if not result:
                return False, "Không tìm thấy xe với biển số này"
            
            vehicle_id = result[0]
            
            # Kiểm tra file có tồn tại không
            if not os.path.exists(image_path):
                return False, f"File ảnh không tồn tại: {image_path}"
            
            # Thêm ảnh mới
            cursor.execute('''
            INSERT INTO plate_images (vehicle_id, image_path)
            VALUES (?, ?)
            ''', (vehicle_id, image_path))
            
            # Thêm vào lịch sử
            cursor.execute('''
            INSERT INTO change_history (vehicle_id, change_type, description)
            VALUES (?, ?, ?)
            ''', (vehicle_id, "UPDATE", f"Thêm ảnh biển số: {os.path.basename(image_path)}"))
            
            conn.commit()
            
            return True, "Thêm ảnh thành công"
            
        except Exception as e:
            logging.error(f"Error adding plate image: {str(e)}")
            traceback.print_exc()
            if conn:
                conn.rollback()
            return False, str(e)
        finally:
            if conn:
                conn.close()
    
    def get_statistics(self):
        """Lấy thống kê từ database"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Tổng số xe
            cursor.execute("SELECT COUNT(*) FROM vehicles")
            total_vehicles = cursor.fetchone()[0]
            
            # Thống kê theo loại xe
            cursor.execute("""
            SELECT vehicle_type, COUNT(*) as count 
            FROM vehicles 
            GROUP BY vehicle_type 
            ORDER BY count DESC
            """)
            types_stats = cursor.fetchall()
            
            # Thống kê theo hãng xe
            cursor.execute("""
            SELECT brand, COUNT(*) as count 
            FROM vehicles 
            GROUP BY brand 
            ORDER BY count DESC 
            LIMIT 10
            """)
            brands_stats = cursor.fetchall()
            
            # Thống kê đăng ký theo tháng
            cursor.execute("""
            SELECT strftime('%m/%Y', register_time) as month, COUNT(*) as count 
            FROM vehicles 
            GROUP BY month 
            ORDER BY register_time DESC 
            LIMIT 12
            """)
            monthly_stats = cursor.fetchall()
            
            # Thống kê theo màu xe
            cursor.execute("""
            SELECT color, COUNT(*) as count
            FROM vehicles
            GROUP BY color
            ORDER BY count DESC
            """)
            color_stats = cursor.fetchall()
            
            # Số lượng ảnh biển số đã lưu
            cursor.execute("SELECT COUNT(*) FROM plate_images")
            total_images = cursor.fetchone()[0]
            
            # Xe mới nhất
            cursor.execute("""
            SELECT plate, owner, register_time 
            FROM vehicles 
            ORDER BY register_time DESC 
            LIMIT 5
            """)
            newest_vehicles = cursor.fetchall()
            
            return {
                'total_vehicles': total_vehicles,
                'types': types_stats,
                'brands': brands_stats,
                'monthly': monthly_stats,
                'colors': color_stats,
                'total_images': total_images,
                'newest_vehicles': newest_vehicles
            }
            
        except Exception as e:
            logging.error(f"Error getting statistics: {str(e)}")
            traceback.print_exc()
            return {
                'total_vehicles': 0,
                'types': [],
                'brands': [],
                'monthly': [],
                'colors': [],
                'total_images': 0,
                'newest_vehicles': []
            }
        finally:
            if conn:
                conn.close()
    
    def import_sample_data(self):
        """Nhập dữ liệu mẫu nếu database trống"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute("PRAGMA foreign_keys = ON")
            cursor = conn.cursor()
            
            # Kiểm tra xem có dữ liệu không
            cursor.execute("SELECT COUNT(*) FROM vehicles")
            count = cursor.fetchone()[0]
            
            if count == 0:
                # Thêm dữ liệu mẫu
                sample_data = [
                    {
                        "plate": "29A-123.45",
                        "owner": "Nguyễn Văn A",
                        "phone": "0912345678",
                        "type": "Sedan",
                        "brand": "Toyota",
                        "color": "Đen",
                        "notes": "Xe đăng ký lần đầu"
                    },
                    {
                        "plate": "30H-678.90",
                        "owner": "Trần Thị B",
                        "phone": "0987654321",
                        "type": "SUV",
                        "brand": "Honda",
                        "color": "Trắng",
                        "notes": "Xe đã qua sử dụng"
                    },
                    {
                        "plate": "33D-789.12",
                        "owner": "Lê Văn C",
                        "phone": "0978123456",
                        "type": "Hatchback",
                        "brand": "Mazda",
                        "color": "Đỏ",
                        "notes": "Xe mới mua"
                    },
                    {
                        "plate": "51F-234.56",
                        "owner": "Phạm Thị D",
                        "phone": "0965432178",
                        "type": "SUV",
                        "brand": "Ford",
                        "color": "Xanh dương",
                        "notes": "Xe công ty"
                    },
                    {
                        "plate": "92A-456.78",
                        "owner": "Hoàng Văn E",
                        "phone": "0932145678",
                        "type": "Sedan",
                        "brand": "Hyundai",
                        "color": "Bạc",
                        "notes": "Xe gia đình"
                    }
                ]
                
                for vehicle in sample_data:
                    self.add_vehicle(
                        plate=vehicle["plate"],
                        owner=vehicle["owner"],
                        phone=vehicle["phone"],
                        vehicle_type=vehicle["type"],
                        brand=vehicle["brand"],
                        color=vehicle["color"],
                        notes=vehicle.get("notes", "")
                    )
                
                return True
            
            return False
            
        except Exception as e:
            logging.error(f"Error importing sample data: {str(e)}")
            traceback.print_exc()
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                conn.close()
    
    def get_vehicle_history(self, vehicle_id):
        """Lấy lịch sử thay đổi của một xe"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
            SELECT id, change_type, change_time, description
            FROM change_history
            WHERE vehicle_id = ?
            ORDER BY change_time DESC
            """, (vehicle_id,))
            
            rows = cursor.fetchall()
            column_names = [desc[0] for desc in cursor.description]
            
            history = []
            for row in rows:
                history_item = dict(zip(column_names, row))
                # Format thời gian
                history_item['change_time'] = datetime.strptime(
                    history_item['change_time'], "%Y-%m-%d %H:%M:%S"
                ).strftime("%d/%m/%Y %H:%M:%S")
                history.append(history_item)
            
            return history
            
        except Exception as e:
            logging.error(f"Error getting vehicle history: {str(e)}")
            traceback.print_exc()
            return []
        finally:
            if conn:
                conn.close()
    
    def get_all_plates(self):
        """Lấy danh sách tất cả các biển số xe"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT plate FROM vehicles ORDER BY register_time DESC")
            plates = [row[0] for row in cursor.fetchall()]
            
            return plates
            
        except Exception as e:
            logging.error(f"Error getting all plates: {str(e)}")
            traceback.print_exc()
            return []
        finally:
            if conn:
                conn.close()
    
    def backup_database(self, backup_path=None):
        """Sao lưu database"""
        conn = None
        try:
            # Nếu không chỉ định đường dẫn backup, tạo tên file mặc định
            if not backup_path:
                backup_dir = os.path.join(os.path.dirname(self.db_path), "backups")
                os.makedirs(backup_dir, exist_ok=True)
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = os.path.join(backup_dir, f"vehicle_registry_backup_{timestamp}.db")
            
            # Mở kết nối tới database gốc
            conn = sqlite3.connect(self.db_path)
            
            # Sao lưu database
            backup_conn = sqlite3.connect(backup_path)
            conn.backup(backup_conn)
            backup_conn.close()
            
            logging.info(f"Database backup created at: {backup_path}")
            return True, backup_path
            
        except Exception as e:
            logging.error(f"Error backing up database: {str(e)}")
            traceback.print_exc()
            return False, str(e)
        finally:
            if conn:
                conn.close()
    
    def restore_database(self, backup_path):
        """Phục hồi database từ file backup"""
        conn = None
        try:
            # Kiểm tra file backup có tồn tại không
            if not os.path.exists(backup_path):
                return False, f"File backup không tồn tại: {backup_path}"
            
            # Tạo bản sao của database hiện tại
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            current_backup = os.path.join(os.path.dirname(self.db_path), f"pre_restore_backup_{timestamp}.db")
            
            # Sao lưu database hiện tại
            success, _ = self.backup_database(current_backup)
            if not success:
                return False, "Không thể tạo bản sao của database hiện tại trước khi phục hồi"
            
            # Mở kết nối tới file backup
            backup_conn = sqlite3.connect(backup_path)
            
            # Mở kết nối tới database chính
            conn = sqlite3.connect(self.db_path)
            
            # Phục hồi database
            backup_conn.backup(conn)
            backup_conn.close()
            
            logging.info(f"Database restored from: {backup_path}")
            return True, "Phục hồi database thành công"
            
        except Exception as e:
            logging.error(f"Error restoring database: {str(e)}")
            traceback.print_exc()
            return False, str(e)
        finally:
            if conn:
                conn.close()
    
    def optimize_database(self):
        """Tối ưu hóa database"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Chạy VACUUM để nén database
            cursor.execute("VACUUM")
            
            # Phân tích lại cấu trúc database
            cursor.execute("ANALYZE")
            
            # Xóa dữ liệu không còn sử dụng
            conn.commit()
            
            logging.info("Database optimized")
            return True, "Tối ưu hóa database thành công"
            
        except Exception as e:
            logging.error(f"Error optimizing database: {str(e)}")
            traceback.print_exc()
            return False, str(e)
        finally:
            if conn:
                conn.close()
    
    def get_setting(self, key, default=None):
        """Lấy giá trị cài đặt từ database"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT setting_value, setting_type FROM app_settings WHERE setting_key = ?", (key,))
            result = cursor.fetchone()
            
            if result:
                value, type_name = result
                
                # Chuyển đổi kiểu dữ liệu
                if type_name == 'boolean':
                    return value.lower() == 'true'
                elif type_name == 'integer':
                    return int(value)
                elif type_name == 'float':
                    return float(value)
                else:
                    return value
            else:
                return default
        except Exception as e:
            logging.error(f"Error getting setting {key}: {str(e)}")
            return default
        finally:
            if conn:
                conn.close()
    
    def set_setting(self, key, value):
        """Cập nhật giá trị cài đặt trong database"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Xác định kiểu dữ liệu
            if isinstance(value, bool):
                setting_type = 'boolean'
                setting_value = 'true' if value else 'false'
            elif isinstance(value, int):
                setting_type = 'integer'
                setting_value = str(value)
            elif isinstance(value, float):
                setting_type = 'float'
                setting_value = str(value)
            else:
                setting_type = 'string'
                setting_value = str(value)
            
            # Cập nhật cài đặt
            cursor.execute("""
            INSERT OR REPLACE INTO app_settings (setting_key, setting_value, setting_type, update_time)
            VALUES (?, ?, ?, datetime('now'))
            """, (key, setting_value, setting_type))
            
            conn.commit()
            
            return True, f"Đã cập nhật cài đặt: {key}"
        except Exception as e:
            logging.error(f"Error setting {key}: {str(e)}")
            if conn:
                conn.rollback()
            return False, str(e)
        finally:
            if conn:
                conn.close()
    
    def get_image_path_by_plate(self, plate):
        """Lấy đường dẫn ảnh cho biển số xe"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Chuẩn hóa biển số
            plate = plate.upper()
            
            # Lấy vehicle_id từ biển số
            cursor.execute("SELECT id FROM vehicles WHERE plate = ?", (plate,))
            result = cursor.fetchone()
            
            if not result:
                return None
            
            vehicle_id = result[0]
            
            # Lấy ảnh mới nhất
            cursor.execute("""
            SELECT image_path FROM plate_images 
            WHERE vehicle_id = ? 
            ORDER BY upload_time DESC LIMIT 1
            """, (vehicle_id,))
            
            result = cursor.fetchone()
            
            if result:
                return result[0]
            else:
                return None
        except Exception as e:
            logging.error(f"Error getting image path: {str(e)}")
            return None
        finally:
            if conn:
                conn.close()
    
    def fix_database_errors(self):
        """Kiểm tra và sửa lỗi cấu trúc database"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute("PRAGMA foreign_keys = OFF")  # Tắt ràng buộc khóa ngoại khi sửa lỗi
            cursor = conn.cursor()
            
            # Kiểm tra tính toàn vẹn của database
            cursor.execute("PRAGMA integrity_check")
            integrity_result = cursor.fetchone()[0]
            
            if integrity_result != "ok":
                logging.error(f"Database integrity check failed: {integrity_result}")
                
                # Sao lưu database lỗi
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = os.path.join(os.path.dirname(self.db_path), f"corrupt_db_backup_{timestamp}.db")
                
                # Sao chép file database
                import shutil
                shutil.copy2(self.db_path, backup_path)
                
                # Tạo database mới
                os.remove(self.db_path)
                self.initialize_db()
                
                return False, f"Database có lỗi cấu trúc và đã được tạo lại. Bản sao của database cũ: {backup_path}"
            
            # Kiểm tra các bảng
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            expected_tables = {'vehicles', 'plate_images', 'change_history', 'app_settings'}
            actual_tables = {row[0] for row in cursor.fetchall() if not row[0].startswith('sqlite_')}
            
            missing_tables = expected_tables - actual_tables
            if missing_tables:
                # Tạo lại các bảng bị thiếu
                self.initialize_db()
                return True, f"Đã tạo lại các bảng bị thiếu: {', '.join(missing_tables)}"
            
            # Nếu tất cả đều ổn
            return True, "Database hoạt động bình thường, không phát hiện lỗi"
            
        except Exception as e:
            logging.error(f"Error fixing database: {str(e)}")
            if conn:
                conn.rollback()
            return False, str(e)
        finally:
            if conn:
                conn.close()
            
    def get_plates_by_owner(self, owner_name):
        """Tìm tất cả xe của một chủ xe"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
            SELECT plate FROM vehicles 
            WHERE owner LIKE ? 
            ORDER BY register_time DESC
            """, (f"%{owner_name}%",))
            
            plates = [row[0] for row in cursor.fetchall()]
            return plates
            
        except Exception as e:
            logging.error(f"Error getting plates by owner: {str(e)}")
            return []
        finally:
            if conn:
                conn.close()
                
    def get_plates_by_phone(self, phone):
        """Tìm tất cả xe dựa trên số điện thoại"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
            SELECT plate FROM vehicles 
            WHERE phone LIKE ? 
            ORDER BY register_time DESC
            """, (f"%{phone}%",))
            
            plates = [row[0] for row in cursor.fetchall()]
            return plates
            
        except Exception as e:
            logging.error(f"Error getting plates by phone: {str(e)}")
            return []
        finally:
            if conn:
                conn.close()
    
    def search_advanced(self, **criteria):
        """Tìm kiếm nâng cao với nhiều tiêu chí"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Xây dựng câu truy vấn động
            query = "SELECT * FROM vehicles WHERE 1=1"
            params = []
            
            if 'plate' in criteria and criteria['plate']:
                query += " AND plate LIKE ?"
                params.append(f"%{criteria['plate']}%")
                
            if 'owner' in criteria and criteria['owner']:
                query += " AND owner LIKE ?"
                params.append(f"%{criteria['owner']}%")
                
            if 'phone' in criteria and criteria['phone']:
                query += " AND phone LIKE ?"
                params.append(f"%{criteria['phone']}%")
                
            if 'vehicle_type' in criteria and criteria['vehicle_type']:
                query += " AND vehicle_type = ?"
                params.append(criteria['vehicle_type'])
                
            if 'brand' in criteria and criteria['brand']:
                query += " AND brand = ?"
                params.append(criteria['brand'])
                
            if 'color' in criteria and criteria['color']:
                query += " AND color = ?"
                params.append(criteria['color'])
                
            if 'start_date' in criteria and criteria['start_date']:
                query += " AND register_time >= ?"
                params.append(criteria['start_date'])
                
            if 'end_date' in criteria and criteria['end_date']:
                query += " AND register_time <= ?"
                params.append(criteria['end_date'])
                
            if 'notes' in criteria and criteria['notes']:
                query += " AND notes LIKE ?"
                params.append(f"%{criteria['notes']}%")
            
            # Sắp xếp và giới hạn
            sort_field = criteria.get('sort_field', 'register_time')
            sort_order = criteria.get('sort_order', 'DESC')
            
            # Kiểm tra tính hợp lệ của sort_field để tránh SQL injection
            allowed_sort_fields = {'id', 'plate', 'owner', 'phone', 'vehicle_type', 'brand', 'color', 'register_time', 'last_update'}
            if sort_field not in allowed_sort_fields:
                sort_field = 'register_time'
                
            # Kiểm tra tính hợp lệ của sort_order
            if sort_order not in ('ASC', 'DESC'):
                sort_order = 'DESC'
                
            query += f" ORDER BY {sort_field} {sort_order}"
            
            # Giới hạn kết quả nếu có
            if 'limit' in criteria and criteria['limit']:
                query += " LIMIT ?"
                params.append(int(criteria['limit']))
                
            if 'offset' in criteria and criteria['offset']:
                query += " OFFSET ?"
                params.append(int(criteria['offset']))
                
            # Thực thi truy vấn
            cursor.execute(query, params)
            
            # Lấy tên cột
            column_names = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            
            # Chuyển đổi dữ liệu thành định dạng tương thích với code hiện tại
            results = []
            for row in rows:
                vehicle = dict(zip(column_names, row))
                
                # Chuyển đổi key names để tương thích với code hiện tại
                vehicle['type'] = vehicle.pop('vehicle_type')
                vehicle['timestamp'] = datetime.strptime(
                    vehicle.pop('register_time'), "%Y-%m-%d %H:%M:%S"
                ).strftime("%d/%m/%Y %H:%M")
                
                # Chỉ lấy ảnh cho xe cụ thể nếu yêu cầu
                if criteria.get('include_images', False):
                    # Lấy ảnh biển số mới nhất
                    cursor.execute("""
                    SELECT image_path FROM plate_images 
                    WHERE vehicle_id = ? 
                    ORDER BY upload_time DESC LIMIT 1
                    """, (vehicle['id'],))
                    
                    image_result = cursor.fetchone()
                    if image_result:
                        vehicle['image_path'] = image_result[0]
                    else:
                        vehicle['image_path'] = None
                
                results.append(vehicle)
            
            return results
            
        except Exception as e:
            logging.error(f"Advanced search error: {str(e)}")
            traceback.print_exc()
            return []
        finally:
            if conn:
                conn.close()
    
    def import_from_excel(self, excel_file):
        """Nhập dữ liệu từ file Excel"""
        conn = None
        try:
            import pandas as pd
            
            # Đọc file Excel
            df = pd.read_excel(excel_file)
            
            # Kiểm tra các cột bắt buộc
            required_columns = {'plate', 'owner', 'phone'}
            columns = set(df.columns)
            
            if not required_columns.issubset(columns):
                missing = required_columns - columns
                return False, f"Thiếu các cột bắt buộc: {', '.join(missing)}"
            
            # Mở kết nối database
            conn = sqlite3.connect(self.db_path)
            conn.execute("PRAGMA foreign_keys = ON")
            
            # Bắt đầu transaction
            conn.execute("BEGIN TRANSACTION")
            
            # Đếm số lượng thêm thành công
            success_count = 0
            error_count = 0
            
            # Xử lý từng dòng
            for _, row in df.iterrows():
                try:
                    # Lấy giá trị các cột bắt buộc
                    plate = str(row['plate']).strip().upper()
                    owner = str(row['owner']).strip()
                    phone = str(row['phone']).strip()
                    
                    # Lấy giá trị các cột tùy chọn với giá trị mặc định
                    vehicle_type = str(row.get('type', 'Sedan')).strip()
                    brand = str(row.get('brand', 'Khác')).strip()
                    color = str(row.get('color', 'Không xác định')).strip()
                    notes = str(row.get('notes', '')).strip()
                    
                    # Kiểm tra biển số có hợp lệ không
                    if not plate or len(plate) < 5:
                        error_count += 1
                        continue
                    
                    # Thêm xe vào database
                    success, _ = self.add_vehicle(plate, owner, phone, vehicle_type, brand, color, notes)
                    
                    if success:
                        success_count += 1
                    else:
                        error_count += 1
                        
                except Exception as row_error:
                    logging.error(f"Error importing row: {str(row_error)}")
                    error_count += 1
                    continue
            
            # Commit transaction nếu thành công
            conn.commit()
            
            return True, f"Đã nhập thành công {success_count} xe. Có {error_count} lỗi."
            
        except Exception as e:
            logging.error(f"Error importing from Excel: {str(e)}")
            traceback.print_exc()
            
            # Rollback nếu có lỗi
            if conn:
                conn.rollback()
                
            return False, str(e)
        finally:
            if conn:
                conn.close()