import sqlite3
import os
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path="database/vehicle_registry.db"):
        self.db_path = db_path
        self.initialize_db()
    
    def initialize_db(self):
        """Tạo database và các bảng nếu chưa tồn tại"""
        # Đảm bảo thư mục tồn tại
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
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
        
        # Tạo index cho tìm kiếm nhanh
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_vehicles_plate ON vehicles (plate)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_vehicles_owner ON vehicles (owner)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_vehicles_phone ON vehicles (phone)')
        
        conn.commit()
        conn.close()
    
    def add_vehicle(self, plate, owner, phone, vehicle_type, brand, color="Không có thông tin", notes=""):
        """Thêm xe mới vào database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
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
            
            conn.close()
            
            return True, new_vehicle
            
        except Exception as e:
            if 'conn' in locals() and conn:
                conn.close()
            return False, str(e)
    
    def update_vehicle(self, plate, **updates):
        """Cập nhật thông tin xe"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Kiểm tra xem xe có tồn tại không
            cursor.execute("SELECT id FROM vehicles WHERE plate = ?", (plate,))
            result = cursor.fetchone()
            if not result:
                conn.close()
                return False, "Không tìm thấy xe với biển số này"
                
            vehicle_id = result[0]
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Chuẩn bị câu lệnh SQL và tham số
            allowed_fields = {'owner': 'owner', 'phone': 'phone', 'vehicle_type': 'type',
                             'brand': 'brand', 'color': 'color', 'notes': 'notes'}
            sql_fields = []
            sql_values = []
            
            for key, value in updates.items():
                db_field = allowed_fields.get(key)
                if db_field:
                    sql_fields.append(f"{key} = ?")
                    sql_values.append(value)
            
            # Thêm thời gian cập nhật
            sql_fields.append("last_update = ?")
            sql_values.append(current_time)
            
            # Thêm id để WHERE clause
            sql_values.append(vehicle_id)
            
            # Cập nhật thông tin xe
            sql_query = f"UPDATE vehicles SET {', '.join(sql_fields)} WHERE id = ?"
            cursor.execute(sql_query, sql_values)
            
            # Thêm vào lịch sử
            cursor.execute('''
            INSERT INTO change_history (vehicle_id, change_type, description)
            VALUES (?, ?, ?)
            ''', (vehicle_id, "UPDATE", f"Cập nhật thông tin xe: {plate}"))
            
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
            
            conn.close()
            
            return True, updated_vehicle
            
        except Exception as e:
            if 'conn' in locals() and conn:
                conn.close()
            return False, str(e)
    
    def delete_vehicle(self, plate):
        """Xóa xe khỏi database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Kiểm tra xem xe có tồn tại không
            cursor.execute("SELECT id FROM vehicles WHERE plate = ?", (plate,))
            result = cursor.fetchone()
            if not result:
                conn.close()
                return False, "Không tìm thấy xe với biển số này"
                
            vehicle_id = result[0]
            
            # Lưu lịch sử trước khi xóa
            cursor.execute('''
            INSERT INTO change_history (vehicle_id, change_type, description)
            VALUES (?, ?, ?)
            ''', (vehicle_id, "DELETE", f"Xóa xe: {plate}"))
            
            # Xóa xe
            cursor.execute("DELETE FROM vehicles WHERE id = ?", (vehicle_id,))
            
            conn.commit()
            conn.close()
            
            return True, "Xóa xe thành công"
            
        except Exception as e:
            if 'conn' in locals() and conn:
                conn.close()
            return False, str(e)
    
    def search_vehicles(self, search_text=None, vehicle_type=None, brand=None, date=None, limit=100):
        """Tìm kiếm xe với nhiều tiêu chí"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            sql_query = "SELECT * FROM vehicles WHERE 1=1"
            sql_params = []
            
            if search_text:
                sql_query += " AND (plate LIKE ? OR owner LIKE ? OR phone LIKE ?)"
                search_pattern = f"%{search_text}%"
                sql_params.extend([search_pattern, search_pattern, search_pattern])
            
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
            
            conn.close()
            return results
            
        except Exception as e:
            if 'conn' in locals() and conn:
                conn.close()
            print(f"Search error: {str(e)}")
            return []
    
    def get_vehicle_by_plate(self, plate):
        """Lấy thông tin xe theo biển số"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
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
                
                conn.close()
                return vehicle
            else:
                conn.close()
                return None
                
        except Exception as e:
            if 'conn' in locals() and conn:
                conn.close()
            print(f"Error getting vehicle: {str(e)}")
            return None
    
    def add_plate_image(self, plate, image_path):
        """Thêm ảnh biển số cho xe"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Lấy vehicle_id từ biển số
            cursor.execute("SELECT id FROM vehicles WHERE plate = ?", (plate,))
            result = cursor.fetchone()
            
            if not result:
                conn.close()
                return False, "Không tìm thấy xe với biển số này"
            
            vehicle_id = result[0]
            
            # Thêm ảnh mới
            cursor.execute('''
            INSERT INTO plate_images (vehicle_id, image_path)
            VALUES (?, ?)
            ''', (vehicle_id, image_path))
            
            conn.commit()
            conn.close()
            
            return True, "Thêm ảnh thành công"
            
        except Exception as e:
            if 'conn' in locals() and conn:
                conn.close()
            return False, str(e)
    
    def get_statistics(self):
        """Lấy thống kê từ database"""
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
            
            conn.close()
            
            return {
                'total_vehicles': total_vehicles,
                'types': types_stats,
                'brands': brands_stats,
                'monthly': monthly_stats
            }
            
        except Exception as e:
            if 'conn' in locals() and conn:
                conn.close()
            print(f"Error getting statistics: {str(e)}")
            return {
                'total_vehicles': 0,
                'types': [],
                'brands': [],
                'monthly': []
            }
    
    def import_sample_data(self):
        """Nhập dữ liệu mẫu nếu database trống"""
        try:
            conn = sqlite3.connect(self.db_path)
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
                    },
                    {
                        "plate": "30H-678.90",
                        "owner": "Trần Thị B",
                        "phone": "0987654321",
                        "type": "SUV",
                        "brand": "Honda",
                        "color": "Trắng",
                    },
                    {
                        "plate": "33D-789.12",
                        "owner": "Lê Văn C",
                        "phone": "0978123456",
                        "type": "Hatchback",
                        "brand": "Mazda",
                        "color": "Đỏ",
                    }
                ]
                
                for vehicle in sample_data:
                    self.add_vehicle(
                        plate=vehicle["plate"],
                        owner=vehicle["owner"],
                        phone=vehicle["phone"],
                        vehicle_type=vehicle["type"],
                        brand=vehicle["brand"],
                        color=vehicle["color"]
                    )
                
                return True
            
            conn.close()
            return False
            
        except Exception as e:
            if 'conn' in locals() and conn:
                conn.close()
            print(f"Error importing sample data: {str(e)}")
            return False