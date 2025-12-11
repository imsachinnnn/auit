"""
Django settings for ssm project.
"""
from pathlib import Path
import os

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-h)g6-a+cdh^rhpxsfhi5#8#a=++iq0z%*61-l%$nh6$^9e+r#s'
DEBUG = True
ALLOWED_HOSTS = ['10.165.244.80', 'localhost', '127.0.0.1','*','401dea466adf.ngrok-free.app']


# --- APPLICATION DEFINITION ---
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'students',
    'staffs',
    "anymail",
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'ssm.middleware.StaticFilesHeadersMiddleware',  # Custom middleware for static file headers
]

# Security settings that might block static files
SECURE_CONTENT_TYPE_NOSNIFF = False  # Allow CSS/JS to load properly
SECURE_BROWSER_XSS_FILTER = False  # Prevent XSS filter from blocking CSS

# Only use WhiteNoise in production (when DEBUG=False)
if not DEBUG:
    MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')

ROOT_URLCONF = 'ssm.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'ssm.wsgi.application'

# --- DATABASE ---
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'students',
        'USER': 'root',
        'PASSWORD': 'dbms',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}

# --- PASSWORD VALIDATION ---
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# --- INTERNATIONALIZATION ---
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# --- STATIC FILES (for CSS, JS of your project and admin) ---
STATIC_URL = '/static/'

# Fix for Windows MIME types issues - CRITICAL for admin CSS
import mimetypes
# Ensure CSS and JS files are recognized with correct MIME types
mimetypes.add_type("text/css", ".css", True)
mimetypes.add_type("text/css", ".css", False)  # Also add without strict
mimetypes.add_type("application/javascript", ".js", True)
mimetypes.add_type("application/javascript", ".js", False)
mimetypes.add_type("text/javascript", ".js", True)

# --- STATIC FILES CONFIGURATION ---
# This tells Django where to look for your main static files folder.
if os.path.exists(os.path.join(BASE_DIR, 'static')):
    STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
else:
    STATICFILES_DIRS = []

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Ensure default static files finders are used (includes admin static files)
# This is the default, but we're being explicit to ensure admin files are found
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# Only set storage in production (WhiteNoise)
# DO NOT set STATICFILES_STORAGE in development - let Django use defaults
if not DEBUG:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
# --- MEDIA FILES (for user-uploaded content) ---
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# --- DEFAULT SETTINGS ---
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
CORS_ALLOWED_ORIGINS = ["null"]

# settings.py

# your_project/settings.py

# Add this for development/testing
#EMAIL_BACKEND = "anymail.backends.mailgun.EmailBackend"
# For production, you would use a real SMTP server:
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.example.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'your-email@example.com'
# EMAIL_HOST_PASSWORD = 'your-email-password'
#login_url = '/students/login/'

# EMAIL_BACKEND = "anymail.backends.mailersend.EmailBackend"

# ANYMAIL = {
#     "MAILGUN_API_KEY": "",
#     "MAILGUN_SENDER_DOMAIN": "sandboxb5c88b3d41574fd2b90292f18775d58e.mailgun.org",  # e.g., mg.yourdomain.com
# }
# # Default from email
# DEFAULT_FROM_EMAIL = "sandboxb5c88b3d41574fd2b90292f18775d58e.mailgun.org" 
# SERVER_EMAIL = "sandboxb5c88b3d41574fd2b90292f18775d58e.mailgun.org" # For error reports
# #LOGIN_URL = 'student_login'

# # settings.py
# from decouple import config

# # Email Configuration with Mailgun
# EMAIL_BACKEND = 'anymail.backends.mailgun.EmailBackend'
# ANYMAIL = {
#     #"MAILGUN_API_KEY": config("774826f10a768fc1a4ca2d5b753e4c5d-8b22cbee-45c2a532"),  # Your Mailgun API key
#     "MAILGUN_SENDER_DOMAIN": config('sandboxb5c88b3d41574fd2b90292f18775d58e.mailgun.org'),
# }
# DEFAULT_FROM_EMAIL = config('sam@sandboxb5c88b3d41574fd2b90292f18775d58e.mailgun.org', default='rash@sandboxb5c88b3d41574fd2b90292f18775d58e.mailgun.org')
# SERVER_EMAIL = DEFAULT_FROM_EMAIL