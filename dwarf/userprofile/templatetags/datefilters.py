
from django import template
from django.template.defaultfilters import stringfilter

from dwarfutils import dateutils

register = template.Library()


@register.filter
@stringfilter
def from_unix_timestamp(value):
    return dateutils.unix_to_datetime(int(value))
