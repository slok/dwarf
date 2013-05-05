import json
import abc

from dwarfutils.redisutils import (get_redis_push_notifications_connection,
                                   get_redis_connection)
from dwarfutils.dateutils import unix_now_utc
from achievements.templatetags.achievementfilters import achievement_image_url


ACHIEVEMENT = 'achievement'
SHORTLINK = 'shortlink'
LEVEL = 'level'


class Notification(object):
    PUSH_KEY_FORMAT = "Push:notifications:{0}"
    STORE_KEY_FORMAT = "Notifications:{0}"
    __metaclass__ = abc.ABCMeta

    def __init__(self,
                 notification_type=None,
                 title=None,
                 description=None,
                 image=None,
                 date=None,
                 user_id=None,
                 key=None,
                 push_key=None):
        self._notification_type = notification_type
        self._title = title
        self._description = description
        self._image = image
        self.date = unix_now_utc()
        self._user_id = user_id

        if not push_key:
            self._push_key = Notification.PUSH_KEY_FORMAT.format(user_id)
        if not key:
            self._key = Notification.STORE_KEY_FORMAT.format(user_id)

    @property
    def notification_type(self):
        return self._notification_type

    @property
    def title(self):
        return self._title

    @property
    def description(self):
        return self._description

    @property
    def image(self):
        return self._image

    @property
    def user_id(self):
        return self._user_id

    @abc.abstractmethod
    def to_json(self):
        return None

    @classmethod
    @abc.abstractmethod
    def from_json(cls, json_dict):
        return None

    def save(self):
        r = get_redis_connection()
        r.zadd(self._key, self.date, self.to_json())

    def send_push(self):
        # Publish in redis
        r = get_redis_push_notifications_connection()
        r.publish(self._push_key, self.to_json())

    @classmethod
    def _notification_factory(cls, json_data):
        """Decides based on the json what notification type needs to create"""
        json_decoded = json.loads(json_data)
        result = None

        # Decide
        if json_decoded['type'] == ACHIEVEMENT:
            result = AchievementNotification.from_json(json_decoded)
        elif json_decoded['type'] == SHORTLINK:
            result = ShortLinkNotification.from_json(json_decoded)
        else:
            raise TypeError("There are no notifications of that type")

        return result

    @classmethod
    def find(cls, user, offset=0, limit=-1, desc=True):
        """The offset starts in 0"""
        r = get_redis_push_notifications_connection()
        func = r.zrange if not desc else r.zrevrange
        key = Notification.STORE_KEY_FORMAT.format(user.id)
        result = map(Notification._notification_factory, func(key, offset, limit))
        return result

    @classmethod
    def time_range(cls, user, lowerbound, upperbound, desc=True):
        """lowbound and upperbound in unixtimestamp"""
        r = get_redis_push_notifications_connection()
        key = Notification.STORE_KEY_FORMAT.format(user.id)
        func = r.zrangebyscore if not desc else r.zrevrangebyscore
        result = map(Notification._notification_factory, func(key, lowerbound, upperbound))
        return result

    @classmethod
    def all(cls, user, desc=True):
        return Notification.find(user, desc=desc)

    @classmethod
    def count(cls, user, min_time="-inf", max_time="+inf"):
        r = get_redis_push_notifications_connection()
        key = Notification.STORE_KEY_FORMAT.format(user.id)
        return int(r.zcount(key, min_time, max_time))


class AchievementNotification(Notification):

    def __init__(self, achievement, user_id=None, user=None):
        if not user_id and user:
            user_id = user.id
        elif not user_id and not user:
            raise AttributeError('userId or User instance needed')

        self._achievement_id = achievement.id
        notification_type = ACHIEVEMENT
        image = achievement_image_url(achievement.image)
        title = "Achievement unlocked!"
        description = "You gained the '{0}' achievement".format(achievement.name)
        super(AchievementNotification, self).__init__(
            notification_type=notification_type,
            title=title,
            description=description,
            image=image,
            user_id=user_id
        )

    @property
    def achievement_id(self):
        return self._achievement_id

    def to_json(self):
        data = {
            'type': self._notification_type,
            'title': self._title,
            'description': self._description,
            'image': self._image,
            'date': self.date,
            'user_id': self._user_id,
            'achievement_id': self._achievement_id
        }
        return json.dumps(data)

    @classmethod
    def from_json(cls, json_dict):
        # Avoid circular dependency of the signals
        from achievements.models import Achievement
        achiev = Achievement.objects.get(id=json_dict['achievement_id'])

        a = AchievementNotification(achiev, user_id=json_dict['user_id'])
        a.date = json_dict['date']

        return a


class ShortLinkNotification(Notification):

    def __init__(self, short_link, user_id=None, user=None):
        if not user_id and user:
            user_id = user.id
        elif not user_id and not user:
            raise AttributeError('userId or User instance needed')

        self._url = short_link.url
        self._token = short_link.token
        self._url_title = short_link.title
        notification_type = SHORTLINK
        image = None
        title = "Link shortened"
        description = "You shortened '{0}' link".format(self._url_title)
        super(ShortLinkNotification, self).__init__(
            notification_type=notification_type,
            title=title,
            description=description,
            image=image,
            user_id=user_id
        )

    @property
    def token(self):
        return self._token

    @property
    def url(self):
        return self._token

    @property
    def url_title(self):
        return self._url_title

    def to_json(self):
        data = {
            'type': self._notification_type,
            'title': self._title,
            'description': self._description,
            'image': self._image,
            'date': self.date,
            'user_id': self._user_id,
            'url': self._url,
            'url_title': self._url_title,
            'token': self._token,
        }
        return json.dumps(data)

    @classmethod
    def from_json(cls, json_dict):
        # Avoid circular dependency of the signals
        from linkshortener.models import ShortLink

        short_link = ShortLink.find(token=json_dict['token'])

        sl = ShortLinkNotification(short_link, user_id=json_dict['user_id'])
        sl.date = json_dict['date']

        return sl
