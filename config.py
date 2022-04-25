import os


# default config
class BaseConfig(object):
    DEBUG = False
    # shortened for readability
    SECRET_KEY = 'banking'


class TestConfig(BaseConfig):
    DEBUG = True
    TESTING = True
    WTF_CSRF_ENABLED = False
    MYSQL_DATABASE_USER = 'root'
    MYSQL_DATABASE_PASSWORD = 'root'
    MYSQL_DATABASE_HOST = 'localhost'
    MYSQL_DATABASE_DB = 'banking'

    # mysql = MySQL()
    # mysql.init_app(app)  # mysql engine start


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class ProductionConfig(BaseConfig):
    DEBUG = False