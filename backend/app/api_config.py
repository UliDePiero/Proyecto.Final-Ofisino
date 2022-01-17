import os
from typing import Union, Type


MISSING = 'MISSING_KEY'


class ProductionConfig:
    SECRET_KEY = os.getenv('APP_SECRET_KEY', MISSING)
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID', MISSING)
    GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET', MISSING)
    DATABASE_URL = os.getenv('DATABASE_URL', MISSING)
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')

    # Open API Config
    OPENAPI_VERSION = "3.0.2"
    OPENAPI_JSON_PATH = "api-spec.json"
    OPENAPI_URL_PREFIX = "/"
    OPENAPI_REDOC_PATH = "/redoc"
    OPENAPI_REDOC_URL = "https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js"
    OPENAPI_SWAGGER_UI_PATH = "/swagger"
    OPENAPI_SWAGGER_UI_URL = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    OPENAPI_RAPIDOC_PATH = "/rapidoc"
    OPENAPI_RAPIDOC_URL = "https://unpkg.com/rapidoc/dist/rapidoc-min.js"


class DevelopmentConfig:
    SECRET_KEY = 'not a secret'
    GOOGLE_CLIENT_ID = '1'
    GOOGLE_CLIENT_SECRET = '2'
    DATABASE_URL = 'sqlite:///./testing.sqlite'
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')

    # Open API Config
    OPENAPI_VERSION = "3.0.2"
    OPENAPI_JSON_PATH = "api-spec.json"
    OPENAPI_URL_PREFIX = "/"
    OPENAPI_REDOC_PATH = "/redoc"
    OPENAPI_REDOC_URL = "https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js"
    OPENAPI_SWAGGER_UI_PATH = "/swagger"
    OPENAPI_SWAGGER_UI_URL = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    OPENAPI_RAPIDOC_PATH = "/rapidoc"
    OPENAPI_RAPIDOC_URL = "https://unpkg.com/rapidoc/dist/rapidoc-min.js"


def get_config() -> Type[Union[DevelopmentConfig, ProductionConfig]]:
    dev = os.getenv('FLASK_ENV') == 'development__'
    return DevelopmentConfig if dev else ProductionConfig
