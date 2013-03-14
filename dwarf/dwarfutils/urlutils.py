import re
import urllib2
import urllib


TITLE_REGEX = "(<title>|<TITLE>)(.*)(</title>|</TITLE>)"


def extract_url_title(url):
    match = re.search(TITLE_REGEX, urllib2.urlopen(url).read())
    return match.group(2)


def percent_encode_url(url):
    return urllib.quote(url, safe="%/:=&?~#+!$,;'@()*[]-")
