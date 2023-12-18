"""
Django settings for mes project.

Generated by 'django-admin startproject' using Django 2.2.14.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os
import datetime

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
from django.utils.translation import ugettext_lazy

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '@(e8hu481p171x)jz!40a$@gt6@_=#2_g-sscjrc531tsxz0(d'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = eval(os.environ.get('DEBUG', 'True'))

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'drf_yasg',  # swagger文档插件    /api/v1/docs/swagger
    'django_filters',
    'production.apps.ProductionConfig',
    'plan.apps.PlanConfig',
    'basics.apps.BasicsConfig',
    'system.apps.SystemConfig',
    'recipe.apps.RecipeConfig',
    'docs.apps.DocsConfig',
    'work_station.apps.WorkStationConfig',
    'datain.apps.DatainConfig'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'mes.middlewares.DisableCSRF',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'mes.middlewares.SyncMiddleware',
]

ROOT_URLCONF = 'mes.urls'
AUTH_USER_MODEL = 'system.User'

REST_FRAMEWORK_EXTENSIONS = {
    # 缓存时间(1小时)
    'DEFAULT_CACHE_RESPONSE_TIMEOUT': 60 * 10,
    # 缓存到哪里 (caches中配置的default)
    'DEFAULT_USE_CACHE': 'default',
}

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'dist'),],
        # 'DIRS': [],
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
# STATICFILES_DIRS = [
#     os.path.join(BASE_DIR, 'dist/static/'),
# ]

WSGI_APPLICATION = 'mes.wsgi.application'

# drf通用配置
REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema',  # 文档
    'DEFAULT_PERMISSION_CLASS': ('rest_framework.permissions.IsAuthenticated',),  # 权限
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
    ) if DEBUG else ('rest_framework_jwt.authentication.JSONWebTokenAuthentication',),  # 认证
    'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework.DjangoFilterBackend',),  # 过滤
    'DEFAULT_PAGINATION_CLASS': 'mes.paginations.DefaultPageNumberPagination',  # 分页
    'DATETIME_FORMAT': "%Y-%m-%d %H:%M:%S",
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.AcceptHeaderVersioning',
}

JWT_AUTH = {
    'JWT_EXPIRATION_DELTA': datetime.timedelta(days=1),
    'JWT_ALLOW_REFRESH': True,
}

LOGGING_DIR = os.environ.get('LOGGING_DIR', os.path.join(BASE_DIR, 'logs'))

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
        'standard': {
            'format': '%(asctime)s [%(threadName)s:%(thread)d] [%(name)s:%(lineno)d] '
                      '[%(module)s:%(funcName)s] [%(levelname)s]- %(message)s'
        },
        'django_request': {
            'format': '%(levelname)s %(asctime)s %(pathname)s %(module)s %(lineno)d %(message)s'
                      ' status_code:%(status_code)d',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'django_db_backends': {
            'format': '%(levelname)s %(asctime)s %(pathname)s %(module)s %(lineno)d %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },

    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        },
        'django_db_backends': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'django_db_backends'
        },
        'django_request': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'django_request'
        },
        'timedRotatingFile': {
            'level': 'DEBUG',
            'class': 'mes.customer_log.CommonTimedRotatingFileHandler',
            'filename': os.path.join(LOGGING_DIR, 'api_log.log'),
            'when': 'midnight',
            'backupCount': 10,
            'formatter': 'standard',
            'interval': 1,
        },
        'errorFile': {
            'level': 'DEBUG',
            'class': 'mes.customer_log.CommonTimedRotatingFileHandler',
            'filename': os.path.join(LOGGING_DIR, 'error.log'),
            'when': 'midnight',
            'backupCount': 10,
            'formatter': 'standard',
            'interval': 1,
        },
        'syncFile': {
            'level': 'DEBUG',
            'class': 'mes.customer_log.CommonTimedRotatingFileHandler',
            'filename': os.path.join(LOGGING_DIR, 'sync.log'),
            'when': 'midnight',
            'backupCount': 10,
            'formatter': 'standard',
            'interval': 1,
        },
        'asyncFile': {
            'level': 'DEBUG',
            'class': 'mes.customer_log.CommonTimedRotatingFileHandler',
            'filename': os.path.join(LOGGING_DIR, 'async.log'),
            'when': 'midnight',
            'backupCount': 10,
            'formatter': 'standard',
            'interval': 1,
        },
        'sendFile': {
            'level': 'DEBUG',
            'class': 'mes.customer_log.CommonTimedRotatingFileHandler',
            'filename': os.path.join(LOGGING_DIR, 'send.log'),
            'when': 'midnight',
            'backupCount': 10,
            'formatter': 'standard',
            'interval': 1,
        },
    },
    'loggers': {
        'django.db.backends': {
            'handlers': ['django_db_backends'],
            'propagate': True,
            'level': 'DEBUG' if DEBUG else 'INFO',
        },
        'django.request': {
            'handlers': ['django_request'],
            'level': 'ERROR',
            'propagate': False,
        },
        'api_log': {
            'handlers': ['timedRotatingFile'],
            'level': 'DEBUG' if DEBUG else 'INFO',
        },
        'error_log': {
            'handlers': ['errorFile'],
            'level': 'DEBUG' if DEBUG else 'INFO',
        },
        'sync_log': {
            'handlers': ['syncFile'],
            'level': 'DEBUG' if DEBUG else 'INFO',
        },
        'async_log': {
            'handlers': ['asyncFile'],
            'level': 'INFO',
        },
        'send_log': {
            'handlers': ['sendFile'],
            'level': 'INFO',
        }
    },
}


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',  # 数据库引擎
        'NAME': os.getenv('SFJ_DATABASE_NAME', 'mes'),  # 数据库名称
        'USER': os.getenv('SFJ_DATABASE_USERNAME', 'root'),  # 用户名
        'PASSWORD': os.getenv('SFJ_DATABASE_PASSWORD', 'mes'),  # 密码
        'HOST': os.getenv('SFJ_DATABASE_HOSTNAME', '10.4.14.6'),  # HOST
        'PORT': os.getenv('SFJ_MONOCLE_API_PORT', '33306'),  # 端口
    },
    'mes': {
        'ENGINE': os.getenv('MES_ENGINE', 'django.db.backends.oracle'),  # 数据库引擎
        'NAME': os.getenv('MES_DATABASE_NAME', 'xe'),  # 数据库名称 SID
        'USER': os.getenv('MES_DATABASE_USERNAME', 'mes'),  # 用户名
        'PASSWORD': os.getenv('MES_DATABASE_PASSWORD', 'mes'),  # 密码
        # 'HOST': os.getenv('MES_DATABASE_HOSTNAME', '10.10.120.40'),  # HOST
        # 'PORT': os.getenv('MES_MONOCLE_API_PORT', '1521'),  # 端口
    },
    # 'default': {
    #         'ENGINE': 'django.db.backends.sqlite3',
    #         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    #     },
    'Z01': {
            'ENGINE': 'sql_server.pyodbc',
            'NAME': 'GZSFJ',
            'HOST': '10.4.23.61',
            'PORT': '1433',
            'USER': 'sa',
            'PASSWORD': '123',
            'OPTIONS': {
                'driver': 'ODBC Driver 17 for SQL Server',
                'MARS_Connection': True,
                },
            },
    'Z02': {
            'ENGINE': 'sql_server.pyodbc',
            'NAME': 'GZSFJ',
            'HOST': '10.4.23.62',
            'PORT': '1433',
            'USER': 'sa',
            'PASSWORD': '123',
            'OPTIONS': {
                'driver': 'ODBC Driver 17 for SQL Server',
                'MARS_Connection': True,
                },
            },
    'Z03': {
            'ENGINE': 'sql_server.pyodbc',
            'NAME': 'GZSFJ',
            'HOST': '10.4.23.63',
            'PORT': '1433',
            'USER': 'sa',
            'PASSWORD': '123',
            'OPTIONS': {
                'driver': 'ODBC Driver 17 for SQL Server',
                'MARS_Connection': True,
                },
            },
    'H-Z04': {
            'ENGINE': 'django.db.backends.oracle',
            'NAME': 'PKSJ',  # 数据库SID
            'USER': 'CUSTOMER',
            'PASSWORD': 'CUSTOMER',
            'HOST':'10.4.23.165',
            'PORT':'1521'
        },
    'Z05': {
        'ENGINE': 'sql_server.pyodbc',
        'NAME': 'GZSFJ',
        'HOST': '10.4.23.65',
        'PORT': '1433',
        'USER': 'sa',
        'PASSWORD': '123',
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
            'MARS_Connection': True,
            },
        },
    'Z06': {
            'ENGINE': 'sql_server.pyodbc',
            'NAME': 'GZSFJ',
            'HOST': '10.4.23.66',
            'PORT': '1433',
            'USER': 'sa',
            'PASSWORD': '123',
            'OPTIONS': {
                'driver': 'ODBC Driver 17 for SQL Server',
                'MARS_Connection': True,
                },
            },
    'Z07': {
            'ENGINE': 'sql_server.pyodbc',
            'NAME': 'GZSFJ',
            'HOST': '10.4.23.67',
            'PORT': '1433',
            'USER': 'sa',
            'PASSWORD': '123',
            'OPTIONS': {
                'driver': 'ODBC Driver 17 for SQL Server',
                'MARS_Connection': True,
                },
            },
    'Z08': {
            'ENGINE': 'sql_server.pyodbc',
            'NAME': 'GZSFJ',
            'HOST': '10.4.23.68',
            'PORT': '1433',
            'USER': 'sa',
            'PASSWORD': '123',
            'OPTIONS': {
                'driver': 'ODBC Driver 17 for SQL Server',
                'MARS_Connection': True,
                },
            },
    'Z11': {
            'ENGINE': 'sql_server.pyodbc',
            'NAME': 'GZSFJ',
            'HOST': '10.4.23.71',
            'PORT': '1433',
            'USER': 'sa',
            'PASSWORD': '123',
            'OPTIONS': {
                'driver': 'ODBC Driver 17 for SQL Server',
                'MARS_Connection': True,
                },
            },
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'my_cache_table', # 设置一个数据库存放缓存的表名
    },
    'OPTIONS':{
            'MAX_ENTRIES': 30,                                       # 最大缓存个数（默认300）
            'CULL_FREQUENCY': 3,                                      # 缓存到达最大个数之后，剔除缓存个数的比例，即：1/CULL_FREQUENCY（默认3），3：表示1/3
        },
        #这边只的是缓存的key：p1:1:func_name
        'KEY_PREFIX': 'p1',                                             # 缓存key的前缀（默认空）
        'VERSION': 1,                                                 # 缓存key的版本（默认1）
        'KEY_FUNCTION':"func_name"                                   # 生成key的函数（默认函数会生成为：【前缀:版本:key】）
}

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#     }
# }


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = False

AUTH_USER_MODEL = 'system.User'
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.environ.get('STATIC_ROOT', os.path.join(BASE_DIR, "static/"))

STATICFILES_DIRS = [
    # os.path.join(BASE_DIR, 'static'),# 项目默认会有的路径，如果你部署的不仅是前端打包的静态文件，项目目录static文件下还有其他文件，最好不要删
    os.path.join(BASE_DIR, "dist/static"),# 加上这条
]

LANGUAGES = (
    ('en-us', ugettext_lazy(u"English")),
    ('zh-hans', ugettext_lazy(u"简体中文")),
)

LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale'),
)

# 跨域允许的请求方式，可以使用默认值，默认的请求方式为:
# from corsheaders.defaults import default_methods
CORS_ALLOW_METHODS = (
    'GET',
    'POST',
    'PUT',
    'PATCH',
    'DELETE',
    'OPTIONS'
)

# 允许跨域的请求头，可以使用默认值，默认的请求头为:
# from corsheaders.defaults import default_headers
# CORS_ALLOW_HEADERS = default_headers

CORS_ALLOW_HEADERS = (
    'XMLHttpRequest',
    'X_FILENAME',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'Pragma',
)

# 跨域请求时，是否运行携带cookie，默认为False
CORS_ALLOW_CREDENTIALS = True
# 允许所有主机执行跨站点请求，默认为False
# 如果没设置该参数，则必须设置白名单，运行部分白名单的主机才能执行跨站点请求
CORS_ORIGIN_ALLOW_ALL = True

# mes同步端口
MES_URL = os.environ.get('MES_URL', 'http://127.0.0.1:8000/')

if DEBUG:
    try:
        from .local_settings import *
    except ImportError:
        pass