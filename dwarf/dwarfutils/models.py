from django.db import models

from dwarfutils.dateutils import datetime_now_utc


class AutoDateTimeField(models.DateTimeField):
        def pre_save(self, model_instance, add):
            return datetime_now_utc()
