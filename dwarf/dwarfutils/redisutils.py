from django.conf import settings
import redis


def get_redis_connection():
    return redis.StrictRedis(connection_pool=settings.REDIS_POOL)


def get_redis_notifications_connection():
    return redis.StrictRedis(connection_pool=settings.REDIS_NOTIFICATIONS_POOL)
