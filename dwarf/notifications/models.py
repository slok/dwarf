import json

from dwarfutils.redisutils import get_redis_notifications_connection
from dwarfutils.dateutils import unix_now_utc
from achievements.templatetags.achievementfilters import achievement_image_url

ACHIEVEMENT = 'achievement'
LEVEL = 'level'


class Notification(object):
    KEY_FORMAT = "push:notifications:{0}"

    def __init__(self,
                 notification_type=None,
                 title=None,
                 description=None,
                 image=None,
                 date=None,
                 user_id=None,
                 key=None):
        self._notification_type = notification_type
        self._title = title
        self._description = description
        self._image = image
        self._date = unix_now_utc()
        self._user_id = user_id

        if not key:
            self._key = Notification.KEY_FORMAT.format(user_id)

    def transform_json(self):
        data = {
            'type': self._notification_type,
            'title': self._title,
            'description': self._description,
            'image': self._image,
            'date': self._date
        }
        return json.dumps(data)

    def save(self):
        pass

    def send_push(self):
        # Publish in redis
        r = get_redis_notifications_connection()
        r.publish(self._key, self.transform_json())


class AchievementNotification(Notification):

    def __init__(self, achievement, user):
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
            user_id=user.id
        )
