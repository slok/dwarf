from django.conf import settings

POINTS_PER_CLICK = getattr(settings, 'POINTS_PER_CLICK', 50)
