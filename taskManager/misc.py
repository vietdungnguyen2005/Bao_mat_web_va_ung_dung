""" misc.py contains miscellaneous functions

    Functions that are used in multiple places in the
    rest of the application, but are not tied to a
    specific area are stored in misc.py
"""

import os
import shutil  # Thư viện thao tác file an toàn
from django.utils.text import get_valid_filename  # Hàm làm sạch tên file của Django


def store_uploaded_file(title, uploaded_file):
    """ Stores a temporary uploaded file on disk """
    
    # Tính toán đường dẫn thư mục upload
    # Sử dụng os.path.join để tương thích tốt với Windows (\) và Linux (/)
    base_dir = os.path.dirname(os.path.realpath(__file__))
    upload_dir_path = os.path.join(base_dir, 'static', 'taskManager', 'uploads')

    if not os.path.exists(upload_dir_path):
        os.makedirs(upload_dir_path)

    # --- FIX A03: Injection & Path Traversal ---
    
    # 1. Làm sạch tên file (Sanitization)
    # Nếu user đặt tên là "hacker/../../file.php", hàm này sẽ đổi thành "hacker_.._file.php"
    # Giúp ngăn chặn Path Traversal và các ký tự đặc biệt gây lỗi shell.
    clean_title = get_valid_filename(title)
    
    # Đường dẫn file đích
    destination_path = os.path.join(upload_dir_path, clean_title)

    # 2. Thay thế os.system("mv ...") bằng shutil.move
    # os.system rất nguy hiểm vì nó thực thi lệnh shell.
    # shutil.move là hàm Python thuần, an toàn và chạy được trên mọi hệ điều hành.
    try:
        # Cố gắng di chuyển file từ thư mục tạm
        shutil.move(uploaded_file.temporary_file_path(), destination_path)
    except AttributeError:
        # Trường hợp file nhỏ nằm trên RAM (InMemoryUploadedFile) thì phải ghi ra đĩa
        with open(destination_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)

    return '/static/taskManager/uploads/%s' % (clean_title)