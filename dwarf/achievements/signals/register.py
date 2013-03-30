from django.contrib.auth.models import User

from achievements.signals import receivers
from achievements.signals import signals


signals.user_signup.connect(receivers.padawan_achievement)
signals.user_login.connect(receivers.login_achievement, sender=User)
