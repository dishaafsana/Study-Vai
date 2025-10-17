import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-^^^v)rv3al^5jb@$@ff-_x7wk9uwj-+f*^2n7an*kb0lv1u(a1"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("DEBUG", "True").lower() == "true"

# Allow all hosts during development. For production, specify allowed hosts.
ALLOWED_HOSTS = []

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# OPENAI_MODEL is optional; when absent, Deepseek can be used as the primary provider
OPENAI_MODEL = os.getenv("OPENAI_MODEL", None)

# Deepseek (primary AI provider) - optional
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_API_BASE = os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com")

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "Groups",
    "notes",
    "routine",
    "users",
    # Add your 'Groups' app here
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "MyProject.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(BASE_DIR, "templates")
        ],  # Look for templates in the 'templates' folder
        "APP_DIRS": True,  # Enable Django to look for templates in app-specific 'templates' folders
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.static",  # Add this for static files
            ],
        },
    },
]

WSGI_APPLICATION = "MyProject.wsgi.application"

# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",  # SQLite database engine
        "NAME": BASE_DIR / "db.sqlite3",  # Path to the SQLite database file
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
LANGUAGE_CODE = "en-us"  # Default language
TIME_ZONE = "UTC"  # Default time zone
USE_I18N = True  # Enable internationalization
USE_TZ = True  # Enable time zone support
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Static files (CSS, JavaScript, Images)
STATIC_URL = "static/"
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static")
]  # Look for static files in the 'static' folder

# Media files
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
#####################################################################################settings.py
AUTH_USER_MODEL = "users.CustomUser"
LOGIN_URL = "users:login"
LOGIN_REDIRECT_URL = "users:profile"
