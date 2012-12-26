from datetime import datetime

from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter
@stringfilter
def from_unix_timestamp(value):
    return datetime.fromtimestamp(int(value))
