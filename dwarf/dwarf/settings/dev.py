from redis import ConnectionPool

from common import *

DEBUG = True
SECRET_KEY = '+0$=sj6m5$c3_(jr+dp7mq$npd+f*hx$dn1z4=p1hr^qc*4o6#'

REDIS_HOST = "127.0.0.1"
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_MAX_CONN = 30

# Custo redis pool for all the application process (shared between threads)
REDIS_POOL = ConnectionPool(host=REDIS_HOST,
                        port=REDIS_PORT,
                        db=0,
                        max_connections=REDIS_MAX_CONN)

BROKER_URL = 'amqp://guest:guest@localhost:5672/'
CELERY_RESULT_BACKEND = "amqp"
