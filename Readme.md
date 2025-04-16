# Hệ thống Quản lý Đăng ký Xe

Ứng dụng desktop giúp quản lý thông tin đăng ký xe, bao gồm các chức năng nhận diện biển số xe, quản lý thông tin chủ xe, và xuất báo cáo.

![Ứng dụng Quản lý Đăng ký Xe]

## Tính năng chính

- **Đăng ký xe mới**: Thêm thông tin về xe và chủ sở hữu
- **Quản lý danh sách xe**: Xem, sửa, xóa thông tin xe đã đăng ký
- **Tìm kiếm và lọc**: Tìm kiếm nhanh chóng theo biển số, chủ xe
- **Nhận diện biển số tự động**: Sử dụng camera hoặc tải lên ảnh 
- **Xuất báo cáo**: Xuất dữ liệu ra các định dạng CSV, Excel, PDF, HTML
- **Giao diện sáng/tối**: Hỗ trợ cả hai chế độ giao diện
- **Cơ sở dữ liệu SQLite**: Lưu trữ dữ liệu dễ dàng

## Cài đặt

### Yêu cầu hệ thống

- Python 3.7 trở lên
- Các thư viện cần thiết (xem phần cài đặt bên dưới)
- Ổ cứng: ít nhất 500MB cho cài đặt và dữ liệu
- RAM: tối thiểu 2GB

### Cài đặt từ mã nguồn

1. **Clone repository**

   ```bash
   git clone https://github.com/PVanHuy/My_Projects.git
   cd vehicle-registration-system
   ```

2. **Tạo môi trường ảo (Virtual Environment)**

   ```bash
   python -m venv venv
   ```

3. **Kích hoạt môi trường ảo**

   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Cài đặt các thư viện phụ thuộc**

   ```bash
   pip install -r requirements.txt
   ```

### Thư viện phụ thuộc chính

- PyQt5: Giao diện người dùng
- QtAwesome: Biểu tượng và icon
- OpenCV (cv2): Xử lý ảnh và nhận diện biển số
- SQLite3: Cơ sở dữ liệu
- Pandas: Xử lý dữ liệu
- ReportLab: Xuất báo cáo PDF
- openpyxl: Xuất báo cáo Excel

## Cách sử dụng

### Khởi động ứng dụng

```bash
python main.py
```

### Màn hình chính

Ứng dụng gồm các tab chính:

1. **Đăng ký xe mới**: Nhập thông tin xe và chủ sở hữu
2. **Danh sách xe**: Xem và quản lý tất cả các xe đã đăng ký
3. **Tra cứu biển số**: Tìm kiếm thông tin xe bằng biển số

### Hướng dẫn sử dụng cơ bản

#### Đăng ký xe mới

1. Nhập thông tin chủ xe và thông tin xe
2. Có thể nhập biển số thủ công hoặc sử dụng tính năng nhận diện biển số tự động
3. Nhấn "Lưu" để hoàn tất đăng ký

#### Tra cứu biển số

1. Nhập biển số xe cần tìm hoặc sử dụng camera để quét biển số
2. Hệ thống sẽ hiển thị thông tin xe nếu tìm thấy

#### Xuất báo cáo

1. Từ màn hình danh sách xe, chọn các xe cần xuất báo cáo
2. Chọn định dạng xuất (CSV, Excel, PDF, HTML)
3. Chọn vị trí lưu file

#### Chuyển đổi giao diện sáng/tối

- Sử dụng nút chuyển đổi giao diện ở thanh công cụ
- Hoặc vào menu Chỉnh sửa > Giao diện

## Tính năng nhận diện biển số

Hệ thống sử dụng OpenCV và các thuật toán xử lý ảnh để nhận diện biển số xe:

1. **Từ file ảnh**: Tải lên ảnh có chứa biển số xe
2. **Từ camera**: Sử dụng camera để quét biển số trực tiếp
3. **Xử lý nâng cao**: Tự động cải thiện chất lượng ảnh để tăng độ chính xác

## Cấu trúc dự án

```
vehicle-registration-system/
├── colors/               # Định nghĩa màu sắc cho ứng dụng
│   └── my_colors.py
├── database/             # Mô-đun quản lý cơ sở dữ liệu
│   ├── db_manager.py
│   └── vehicle_model.py
├── recognition/          # Mô-đun nhận diện biển số xe
│   ├── license_plate_recognizer.py
│   └── ...
├── ui/                   # Mô-đun giao diện người dùng
│   ├── list_tab.py
│   ├── main_window.py
│   ├── register_tab.py
│   ├── search_tab.py
│   └── style.py
├── utils/                # Công cụ tiện ích
│   ├── app_icons.py
│   ├── plate_recognition.py
│   ├── theme_manager.py
│   └── theme_switch.py
├── app.py                # Class ứng dụng chính
├── main.py               # Entry point để chạy ứng dụng
└── requirements.txt      # Danh sách các thư viện cần thiết
```

## Gỡ lỗi

### Lỗi thường gặp và cách khắc phục

1. **Không nhận diện được biển số**
   - Kiểm tra chất lượng ảnh, đảm bảo biển số rõ ràng
   - Điều chỉnh ánh sáng phù hợp khi sử dụng camera

2. **Lỗi khi xuất báo cáo PDF**
   - Đảm bảo đã cài đặt ReportLab
   - Kiểm tra quyền truy cập vào thư mục xuất file

3. **Giao diện hiển thị không đúng**
   - Đảm bảo đã cài đặt đầy đủ PyQt5
   - Thử chuyển đổi giữa chế độ sáng và tối

## Đóng góp và phát triển

Nếu bạn muốn đóng góp vào dự án:

1. Fork repository
2. Tạo branch mới (`git checkout -b feature/new-feature`)
3. Commit thay đổi của bạn (`git commit -m 'Add new feature'`)
4. Push lên branch (`git push origin feature/new-feature`)
5. Tạo Pull Request

## Liên hệ

Nếu có bất kỳ câu hỏi hoặc đề xuất, vui lòng liên hệ:

- GitHub: [PVanHuy](https://github.com/PVanHuy)