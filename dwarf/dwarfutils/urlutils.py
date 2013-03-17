import re
import urllib2
import urllib
from urlparse import urlsplit


TITLE_REGEX = "(<title>|<TITLE>)(.*)(</title>|</TITLE>)"


def extract_url_title(url):
    match = re.search(TITLE_REGEX, urllib2.urlopen(url).read())
    return match.group(2)


def extract_url_host(url):
    return urlsplit(url).hostname


def percent_encode_url(url):
    return urllib.quote(url, safe="%/:=&?~#+!$,;'@()*[]-")
