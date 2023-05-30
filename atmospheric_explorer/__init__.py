"""Atmospheric Explorer"""

__version__ = "0.1.0.dev0"

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console':{
            'class':'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {
            'class':'logging.FileHandler',
            'formatter': 'verbose',
            'encoding':'utf-8',
            'filename':'example.log'
        }
    },
    'loggers': {
        'mainlogger': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG'
        }
    }
}