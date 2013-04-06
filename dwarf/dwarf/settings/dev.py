import os

from redis import ConnectionPool

from common import *

DEBUG = True
SECRET_KEY = '+0$=sj6m5$c3_(jr+dp7mq$npd+f*hx$dn1z4=p1hr^qc*4o6#'

REDIS_HOST = "127.0.0.1"
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_MAX_CONN = 30

#Redis settings for push notifications
REDIS_NOTIFICATIONS_HOST = "127.0.0.1"
REDIS_NOTIFICATIONS_PORT = 6379
REDIS_NOTIFICATIONS_DB = 0
REDIS_NOTIFICATIONS_MAX_CONN = 10

# Get geoip data path
GEOIP_PATH = os.getenv("GEOIP_PATH")
if not GEOIP_PATH:
    GEOIP_PATH = "/var/lib/geoip"

# Custom redis pool for all the application process (shared between threads)
REDIS_POOL = ConnectionPool(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    max_connections=REDIS_MAX_CONN
)

# Custom redis pool for push notifications
REDIS_NOTIFICATIONS_POOL = ConnectionPool(
    host=REDIS_NOTIFICATIONS_HOST,
    port=REDIS_NOTIFICATIONS_PORT,
    db=REDIS_NOTIFICATIONS_DB,
    max_connections=REDIS_NOTIFICATIONS_MAX_CONN
)

BROKER_URL = 'amqp://guest:guest@localhost:5672/'
CELERY_RESULT_BACKEND = "amqp"
