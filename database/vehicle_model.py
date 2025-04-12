from datetime import datetime
from database.db_manager import DatabaseManager

def create_vehicle(plate, owner, phone, vehicle_type, brand, color="Không có thông tin", notes=""):
    """
    Creates a new vehicle entry with the given information.
    
    Args:
        plate (str): License plate number
        owner (str): Vehicle owner name
        phone (str): Owner's phone number
        vehicle_type (str): Type of vehicle (e.g., Sedan, SUV)
        brand (str): Vehicle manufacturer (e.g., Toyota, Honda)
        color (str, optional): Vehicle color. Defaults to "Không có thông tin".
        notes (str, optional): Additional notes. Defaults to "".
    
    Returns:
        dict: A new vehicle entry with all information and timestamp
    """
    # Sử dụng database manager để thêm xe
    db = DatabaseManager()
    success, result = db.add_vehicle(
        plate=plate,
        owner=owner,
        phone=phone,
        vehicle_type=vehicle_type,
        brand=brand,
        color=color,
        notes=notes
    )
    
    if success:
        return result
    else:
        raise Exception(f"Không thể thêm xe: {result}")

def update_vehicle(vehicle_data, plate, **updates):
    """
    Updates an existing vehicle in the data list.
    
    Args:
        vehicle_data (list): List of vehicle dictionaries (không còn sử dụng)
        plate (str): License plate number to identify the vehicle
        **updates: Keyword arguments for fields to update
    
    Returns:
        bool: True if the vehicle was found and updated, False otherwise
    """
    # Sử dụng database manager để cập nhật xe
    db = DatabaseManager()
    success, result = db.update_vehicle(plate, **updates)
    
    if success:
        # Cập nhật lại vehicle_data nếu cần
        if isinstance(vehicle_data, list) and isinstance(result, dict):
            for i, vehicle in enumerate(vehicle_data):
                if vehicle["plate"] == plate:
                    vehicle_data[i] = result
                    break
        return True
    else:
        return False

def delete_vehicle(vehicle_data, plate):
    """
    Deletes a vehicle from the data list.
    
    Args:
        vehicle_data (list): List of vehicle dictionaries
        plate (str): License plate number to identify the vehicle
    
    Returns:
        bool: True if the vehicle was found and deleted, False otherwise
    """
    # Sử dụng database manager để xóa xe
    db = DatabaseManager()
    success, result = db.delete_vehicle(plate)
    
    if success:
        # Cập nhật lại vehicle_data nếu cần
        if isinstance(vehicle_data, list):
            for i, vehicle in enumerate(vehicle_data):
                if vehicle["plate"] == plate:
                    del vehicle_data[i]
                    break
        return True
    else:
        return False

def find_vehicle(vehicle_data, plate=None, owner=None, phone=None):
    """
    Finds vehicles matching the provided criteria.
    
    Args:
        vehicle_data (list): List of vehicle dictionaries
        plate (str, optional): License plate to search for. Defaults to None.
        owner (str, optional): Owner name to search for. Defaults to None.
        phone (str, optional): Phone number to search for. Defaults to None.
    
    Returns:
        list: List of vehicles matching the criteria
    """
    # Sử dụng database manager để tìm kiếm xe
    db = DatabaseManager()
    search_text = None
    
    if plate:
        search_text = plate
    elif owner:
        search_text = owner
    elif phone:
        search_text = phone
    
    results = db.search_vehicles(search_text=search_text)
    return results

def export_to_csv(vehicle_data, filename):
    """
    Exports vehicle data to a CSV file.
    
    Args:
        vehicle_data (list): List of vehicle dictionaries
        filename (str): Path to save the CSV file
    
    Returns:
        bool: True if export was successful, False otherwise
    """
    try:
        import csv
        
        # Sử dụng database manager để lấy dữ liệu mới nhất
        db = DatabaseManager()
        vehicles = db.search_vehicles(limit=1000)
        
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            # Write header
            writer.writerow([
                "STT", "Biển số", "Chủ xe", "Số điện thoại", 
                "Loại xe", "Hãng xe", "Màu xe", "Thời gian đăng ký"
            ])
            
            # Write data
            for i, vehicle in enumerate(vehicles, start=1):
                writer.writerow([
                    i,
                    vehicle["plate"],
                    vehicle["owner"],
                    vehicle["phone"],
                    vehicle["type"],
                    vehicle["brand"],
                    vehicle.get("color", "Không có thông tin"),
                    vehicle["timestamp"]
                ])
        
        return True
    except Exception as e:
        print(f"Error exporting to CSV: {str(e)}")
        return False

def export_to_excel(vehicle_data, filename):
    """
    Exports vehicle data to an Excel file.
    
    Args:
        vehicle_data (list): List of vehicle dictionaries
        filename (str): Path to save the Excel file
    
    Returns:
        bool: True if export was successful, False otherwise
    """
    try:
        import pandas as pd # type: ignore
        
        # Sử dụng database manager để lấy dữ liệu mới nhất
        db = DatabaseManager()
        vehicles = db.search_vehicles(limit=1000)
        
        # Convert to DataFrame
        data = []
        for i, vehicle in enumerate(vehicles, start=1):
            data.append([
                i,
                vehicle["plate"],
                vehicle["owner"],
                vehicle["phone"],
                vehicle["type"],
                vehicle["brand"],
                vehicle.get("color", "Không có thông tin"),
                vehicle["timestamp"]
            ])
        
        # Create DataFrame
        columns = ["STT", "Biển số", "Chủ xe", "Số điện thoại", 
                  "Loại xe", "Hãng xe", "Màu xe", "Thời gian đăng ký"]
        
        df = pd.DataFrame(data, columns=columns)
        
        # Export to Excel
        df.to_excel(filename, index=False)
        
        return True
    except Exception as e:
        print(f"Error exporting to Excel: {str(e)}")
        return False

def import_from_csv(filename):
    """
    Imports vehicle data from a CSV file.
    
    Args:
        filename (str): Path to the CSV file
    
    Returns:
        list: List of vehicle dictionaries imported from the CSV
    """
    try:
        import csv
        
        vehicle_data = []
        db = DatabaseManager()
        
        with open(filename, mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header
            
            for row in reader:
                if len(row) >= 7:  # Ensure row has enough columns
                    plate = row[1]
                    owner = row[2]
                    phone = row[3]
                    vehicle_type = row[4]
                    brand = row[5]
                    color = row[6] if len(row) > 6 else "Không có thông tin"
                    
                    # Thêm vào database
                    success, result = db.add_vehicle(
                        plate=plate,
                        owner=owner,
                        phone=phone,
                        vehicle_type=vehicle_type,
                        brand=brand,
                        color=color
                    )
                    
                    if success and isinstance(result, dict):
                        vehicle_data.append(result)
        
        return vehicle_data
    except Exception as e:
        print(f"Error importing from CSV: {str(e)}")
        return []