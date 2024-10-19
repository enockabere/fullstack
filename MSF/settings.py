from pathlib import Path
import os
from decouple import config, Csv
from requests import Session
from zeep import Client
from ms_identity_web.configuration import AADConfig
from ms_identity_web import IdentityWebPython

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


AAD_CONFIG = AADConfig.parse_json(file_path="aad.config.json")
MS_IDENTITY_WEB = IdentityWebPython(AAD_CONFIG)
ERROR_TEMPLATE = "auth/{}.html"


SECRET_KEY = config("SECRET_KEY")
DEBUG = config("DEBUG", default=False, cast=bool)
ALLOWED_HOSTS = [".localhost", ".127.0.0.1", ".172.190.166.156", ".appdev.msf.or.ke"]


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "base",
    "myRequest",
    "dashboard",
    "authentication",
    "HR",
    "approvals",
    "documentation",
]


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
]

MIDDLEWARE.append("ms_identity_web.django.middleware.MsalMiddleware")

if config("MODE") == "prod":
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_BROWSER_XSS_FILTER = True
    SESSION_COOKIE_HTTPONLY = True
    CSRF_COOKIE_HTTPONLY = True
    CONTENT_SECURITY_POLICY = "default-src 'self'; script-src 'self'; style-src 'self';"

    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql_psycopg2",
            "NAME": config("DB_NAME"),
            "USER": config("DB_USER"),
            "PASSWORD": config("DB_PASSWORD"),
            "HOST": config("DB_HOST"),
            "PORT": "",
        }
    }

else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": "MSF_ESS",
        }
    }

ROOT_URLCONF = "MSF.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "MSF.wsgi.application"


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
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATIC_URL = "/selfservice/static/"
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),  # Your root static folder
    os.path.join(BASE_DIR, "frontend", "static"),  # Your frontend static folder
]


MEDIA_URL = "/selfservice/media/"

MEDIA_ROOT = os.path.join(BASE_DIR, "media")


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

ENCRYPT_KEY = b"8zUwJvYZKzgecbudNa7zjhsjTDW-79fwwtUHQn8YCos="


AUTHS = Session()

WEB_SERVICE_UID = config("WEB_SERVICE_UID")
WEB_SERVICE_PWD = config("WEB_SERVICE_PWD")


O_DATA = "http://172.190.166.156:2248/MSFEA/ODataV4/Company('MWA'){}"
BASE_URL = 'http://172.190.166.156:2247/MSFEA/WS/MWA/Codeunit/CuSelfService'

AZURE_AD_CLIENT_ID = config("AZURE_AD_CLIENT_ID")
AZURE_AD_CLIENT_SECRET = config("AZURE_AD_CLIENT_SECRET")
AZURE_AD_REDIRECT_URI = "https://appdev.msf.or.ke/selfservice/auth/redirect"
AZURE_AD_TENANT_ID = config("AZURE_AD_TENANT_ID")
