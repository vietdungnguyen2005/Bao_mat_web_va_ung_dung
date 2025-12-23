# settings.py - PHIÊN BẢN ĐÃ BẢO MẬT (SECURE)
import os
from pathlib import Path
from dotenv import load_dotenv 

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

env_path = os.path.join(BASE_DIR, '.env')
load_dotenv(dotenv_path=env_path)

# ==============================================================================
# A02 & A05: FIX BẢO MẬT CẤU HÌNH (CONFIGURATION HARDENING)
# ==============================================================================

# FIX A02: Không hardcode Secret Key. Lấy từ biến môi trường.
# Fallback cho development (nhưng trên Render BẮT BUỘC phải set biến môi trường)
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'dev-secret-key-change-in-production-!!!!')

# FIX A05: Tắt Debug mode trên môi trường Production.
# Lưu ý: os.getenv trả về chuỗi, cần so sánh để lấy giá trị Boolean.
DEBUG = os.getenv('DJANGO_DEBUG', 'False') == 'True'

# Khi tắt Debug, bắt buộc phải khai báo ALLOWED_HOSTS
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '*.onrender.com', 'nt213bmwvud.live', 'www.nt213bmwvud.live', '*']


# Application definition
INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'taskManager'
)

# Cập nhật cho Django 5.0 (Dùng list thay vì tuple cho dễ nhìn)
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',  # Thêm cho bảo mật
    'whitenoise.middleware.WhiteNoiseMiddleware',     # Thêm cho static files trên Render
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'taskManager.urls'
WSGI_APPLICATION = 'taskManager.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# ==============================================================================
# FIX A02: XÓA BỎ THUẬT TOÁN BĂM MD5
# ==============================================================================
# Code cũ ép dùng MD5PasswordHasher (Kém an toàn).
# Đã XÓA dòng PASSWORD_HASHERS để Django tự dùng PBKDF2 (Mặc định an toàn).


# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')  # Bắt buộc cho collectstatic trên Render
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "static"),
)

# WhiteNoise configuration cho production
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Templates (Cấu hình chuẩn cho Django hiện đại)
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

LOGIN_URL = '/taskManager/login/'
LOGOUT_REDIRECT_URL = '/taskManager/'

# ==============================================================================
# FIX A02 & A05: CẤU HÌNH SESSION & COOKIE AN TOÀN
# ==============================================================================

SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"
SESSION_SERIALIZER = 'django.contrib.sessions.serializers.JSONSerializer'

# FIX: Chặn Javascript đọc Cookie (Chống XSS lấy cắp phiên)
SESSION_COOKIE_HTTPONLY = True 

# Chỉ bật các tính năng này khi chạy thật (DEBUG = False) để tránh lỗi localhost
if not DEBUG:
    # Chỉ gửi cookie qua kết nối HTTPS an toàn
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    
    # Ép buộc chuyển hướng HTTP sang HTTPS
    SECURE_SSL_REDIRECT = True
    
    # HSTS: Ép trình duyệt ghi nhớ dùng HTTPS trong 1 năm
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    
    # Chống tấn công Clickjacking
    X_FRAME_OPTIONS = 'DENY'

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'
# ==============================================================================
# EMAIL CONFIGURATION (GMAIL)
# ==============================================================================
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False

# Lấy thông tin từ biến môi trường để bảo mật
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER') 
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# ==============================================================================
# LOGGING CONFIGURATION (Giữ nguyên của bạn vì nó khá tốt)
# ==============================================================================
LOGS_DIR = os.path.join(BASE_DIR, 'logs')
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {name} {message}',
            'style': '{',
        },
        'security': {
            'format': '[SECURITY] {asctime} | {levelname} | {message}',
            'style': '{',
        },
    },
    'handlers': {
        'security_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'security.log'),
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 5,
            'formatter': 'security',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'security': {
            'handlers': ['security_file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    },
}

#EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'