
from django import template
from django.template.defaultfilters import stringfilter
from achievements import settings

register = template.Library()


@register.filter(name='achievement_image')
@stringfilter
def achievement_image_url(achievement_image):
    return settings.ACHIEVEMENT_IMG_URL_FORMAT.format(achievement_image)
