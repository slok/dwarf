
from common import *

DEBUG = True

REDIS_HOST = "127.0.0.1"
REDIS_PORT = 6379
REDIS_DB = 0

BROKER_URL = 'amqp://guest:guest@localhost:5672/'
CELERY_RESULT_BACKEND = "amqp"
