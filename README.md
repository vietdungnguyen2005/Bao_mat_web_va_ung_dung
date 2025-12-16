# django.nV

django.nV là một ứng dụng Django có chủ ý để lộ các lỗ hổng bảo mật, được cung cấp bởi [nVisium](https://www.nvisium.com/).

## Yêu cầu hệ thống

- Python 3.12
- Django 5.2.9
- pip (package manager)
- virtualenv

Trên macOS, có thể cài đặt Python bằng Homebrew:
```bash
brew install python3
```

Nếu gặp lỗi về PYTHONPATH xung đột, hãy cập nhật biến môi trường:
```bash
export PYTHONPATH="/usr/local/lib/python3.4/site-packages"
```

## Hướng dẫn cài đặt

### 1. Cài đặt virtualenv

Cài đặt virtualenv bằng pip:
```bash
pip install virtualenv
```

### 2. Tạo môi trường ảo (Virtual Environment)

Tạo môi trường ảo với Python 3:
```bash
virtualenv -p python3 venv
```

hoặc trên Windows:
```bash
python -m venv venv
```

### 3. Kích hoạt môi trường ảo

#### Trên CMD (Windows):
```cmd
venv\Scripts\activate
```

#### Trên Git Bash (Windows):
```bash
source venv/Scripts/activate
```

#### Trên Linux/macOS:
```bash
source venv/bin/activate
```

**Lưu ý:** Khi môi trường ảo được kích hoạt, bạn sẽ thấy `(venv)` xuất hiện trước dấu nhắc lệnh.

Để thoát khỏi môi trường ảo, chỉ cần gõ:
```bash
deactivate
```

### 4. Cài đặt các thư viện phụ thuộc

Sau khi kích hoạt môi trường ảo, cài đặt các thư viện cần thiết:
```bash
pip install -r requirements.txt
```

### 5. Migrations

**⚠️ LƯU Ý QUAN TRỌNG:** Migrations đã được tạo sẵn và commit vào repository.

- **KHÔNG CẦN** chạy `python manage.py makemigrations` trừ khi bạn đã xóa các file trong thư mục `taskManager/migrations/`
- Chỉ cần chạy lại `python manage.py makemigrations` khi:
  - Bạn đã xóa các file migration
  - Bạn thay đổi models và cần tạo migration mới

### 6. Thiết lập cơ sở dữ liệu

django.nV cung cấp script tự động tạo và điền dữ liệu vào database. Script này có tên là `reset_db.sh`.

**Trên Linux/macOS hoặc Git Bash:**
```bash
./reset_db.sh
```

**Trên Windows CMD:**
```cmd
python manage.py migrate
python manage.py loaddata fixtures/users.json
python manage.py loaddata fixtures/usersProfiles.json
python manage.py loaddata fixtures/taskManagerProjects.json
python manage.py loaddata fixtures/taskManagerTasks.json
python manage.py loaddata fixtures/taskManagerNotes.json
```

**Lưu ý:** Bạn có thể sử dụng script này để reset database bất cứ khi nào cần.

### 7. Chạy ứng dụng

**Trên Linux/macOS hoặc Git Bash:**
```bash
./runapp.sh
```

**Trên Windows CMD:**
```cmd
python manage.py runserver
```

Sau đó, bạn có thể truy cập ứng dụng web tại: `http://localhost:8000/`

## Tutorials

django.nV đi kèm với một loạt các hướng dẫn về các lỗ hổng bảo mật đã được thêm vào code. Mỗi tutorial bao gồm:
- Mô tả về lỗ hổng
- Gợi ý về vị trí lỗ hổng
- Chi tiết về bug và cách khắc phục

Bạn có thể truy cập các tutorials tại: `http://localhost:8000/taskManager/tutorials/`

Hoặc click vào link "Tutorials" ở góc trên bên phải của giao diện web.

## Mail Server

Ứng dụng chỉ gửi email cho tính năng "Forgot Password". Vì Python 3.12 đã loại bỏ module `smtpd`, chúng ta sử dụng `aiosmtpd` (đã có trong requirements.txt):

```bash
python -m aiosmtpd -n -l localhost:1025
```

Nếu muốn sử dụng mailserver riêng, hãy thêm cấu hình vào file `taskManager/settings.py`.

## Kiểm tra phiên bản Django

Để kiểm tra phiên bản Django đang sử dụng:

```bash
python -m django --version
```

hoặc trong Python shell:
```python
import django
print(django.get_version())
```

## Cấu trúc thư mục chính

```
├── manage.py              # Django management script
├── requirements.txt       # Python dependencies
├── reset_db.sh           # Database reset script
├── runapp.sh             # Application run script
├── fixtures/             # Initial data for database
├── taskManager/          # Main application
│   ├── models.py        # Database models
│   ├── views.py         # Views/Controllers
│   ├── urls.py          # URL routing
│   ├── settings.py      # Django settings
│   ├── migrations/      # Database migrations
│   ├── static/          # Static files (CSS, JS, images)
│   └── templates/       # HTML templates
```

## Lưu ý

- Đây là một ứng dụng có chủ ý để lộ các lỗ hổng bảo mật nhằm mục đích học tập
- **KHÔNG** triển khai ứng dụng này lên môi trường production
- Chỉ sử dụng cho mục đích nghiên cứu và học tập về bảo mật ứng dụng web

---

## English Version

### System Requirements & Setup 

First, make sure Python 3.4+ is installed on your machine. On macOS, this can be installed with Homebrew (eg. `brew install python3`).

Before using django.nV, you'll also need to install virtualenv using pip: `pip install virtualenv`

### Creating Virtual Environment

To set up the repository, use `virtualenv -p python3 venv`, which will create a virtualenv using Python 3.

**Activating Virtual Environment:**

On CMD (Windows):
```cmd
venv\Scripts\activate
```

On Git Bash (Windows):
```bash
source venv/Scripts/activate
```

On Linux/macOS:
```bash
source venv/bin/activate
```

To deactivate: `deactivate`

### Installation of Dependencies

To install the dependencies: `pip install -r requirements.txt`

### Migrations

**⚠️ IMPORTANT:** Migrations are already created and committed to the repository.
- **NO NEED** to run `python manage.py makemigrations` unless you've deleted files in `taskManager/migrations/`
- Only run `python manage.py makemigrations` again if you've deleted migration files or modified models

### Database Setup

Run the reset script: `./reset_db.sh` (Linux/macOS/Git Bash)

Or manually on Windows CMD:
```cmd
python manage.py migrate
python manage.py loaddata fixtures/users.json
python manage.py loaddata fixtures/usersProfiles.json
python manage.py loaddata fixtures/taskManagerProjects.json
python manage.py loaddata fixtures/taskManagerTasks.json
python manage.py loaddata fixtures/taskManagerNotes.json
```

### Running the application

Run: `./runapp.sh` or `python manage.py runserver`

Access at: `http://localhost:8000/`

### Tutorials

Access tutorials at: `http://localhost:8000/taskManager/tutorials/`

### Mail Server

For "Forgot Password" feature (using `aiosmtpd` since `smtpd` is removed in Python 3.12):
```bash
python -m aiosmtpd -n -l localhost:1025
```
