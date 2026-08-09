from os import environ


class Config(object):
    DEBUG = False
    TESTING = False
    SECRET_KEY = environ.get('SECRET_KEY', 'change-me-before-production-use-a-random-50-char-string')

    SESSION_COOKIE_SECURE = True

    WTF_CSRF_ENABLED = environ.get('WTF_CSRF_ENABLED', 'True').lower() in ['true', '1', 't', 'y', 'yes']

    # Instance-wide safety lock: blocks create/update/delete (including setup and
    # user/password changes). Login, logout, import, and export remain allowed.
    READ_ONLY_MODE = environ.get('READ_ONLY_MODE', 'False').lower() in ['true', '1', 't', 'y', 'yes']

    APP_NAME = environ.get('APP_NAME', 'InfraBox')
    APP_LOGGING = environ.get('APP_LOGGING', 'INFO')

    DATA_DIR = environ.get('DATA_DIR', 'data')


class ProductionConfig(Config):
    TESTING = False


class DevelopmentConfig(Config):
    DEBUG = True
    SESSION_COOKIE_SECURE = False


class TestingConfig(Config):
    TESTING = True
    SESSION_COOKIE_SECURE = False
