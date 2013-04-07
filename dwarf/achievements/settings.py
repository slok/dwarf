from django.conf import settings


ACHIEVEMENT_IMG_URL_FORMAT = getattr(settings,
                'ACHIEVEMENT_IMG_URL_FORMAT',
                "https://raw.github.com/ushahidi/Badges/master/Ushahidi/{0}")
