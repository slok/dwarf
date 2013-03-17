
from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

GOOGLE_FAVICON = {
    'host': "http://www.google.com/s2/favicons?domain={0}",
    'url': "http://www.google.com/s2/favicons?domain_url={0}",
}


@register.filter(name='host_favicon')
@stringfilter
def google_host_favicon_url(host):
    return GOOGLE_FAVICON['host'].format(host)


@register.filter(name='url_favicon')
@stringfilter
def google_url_favicon_url(url):
    return GOOGLE_FAVICON['url'].format(url)
