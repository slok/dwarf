from django.contrib.gis.geoip import GeoIP

from requestdataextractor.settings import (OS_CATALOG, BROWSER_CATALOG,
                                         OS_DETAILED, OS_OTHER, BROWSER_OTHER)

# IMPORTANT!!
# We can't use regex because some browsers have different form of header.
# Others have the same structure like Firefox and Chrome.
#
# example:
#   * Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.7 (KHTML, like Gecko)
#   Chrome/16.0.912.75 Safari/535.7
#   * Mozilla/5.0 (X11; Linux x86_64; rv:17.0) Gecko/17.0 Firefox/17.0
#   * Opera/9.80 (X11; Linux x86_64) Presto/2.12.388 Version/12.11
#   * Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)
#   * Mozilla/5.0 (compatible; Konqueror/4.5; Linux) KHTML/4.5.5 (like Gecko)


def detect_browser(http_user_agent):
    """Detects the browser in the header 'http_user_agent' of a request

    :param http_user_agent: The string of the request header http_user_agent
    """
    browser = BROWSER_OTHER

    # check every registered browser
    for i in BROWSER_CATALOG:
        if i.lower() in http_user_agent.lower():
            browser = i
            break

    return browser


def detect_OS(http_user_agent):
    """Detects the OS in the header 'http_user_agent' of a request

    :param http_user_agent: The string of the request header http_user_agent
    """
    os = OS_OTHER

    # check every registered browser
    for i in OS_CATALOG:
        if i.lower() in http_user_agent.lower():
            os = i
            break

    return os


def detect_browser_and_OS(http_user_agent):
    """Detects OS and browser information. Returns a tumple with 3 values:
    (OS, Browser, OS_detail). For example:

    * 'Mozilla/5.0 (X11; Linux x86_64; rv:17.0) Gecko/17.0 Firefox/17.0'

    returns: ("Linux", "Firefox", "Linux x86_64")

    * 'Mozilla/5.0 (iPhone; CPU iPhone OS 6_0_1 like Mac OS X) Apple WebKit
       536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A523 Safari/8536.25
       Safari/8536.25

    returns: ("IOS", "Safari", "IPhone")

    :param http_user_agent: The string of the request header http_user_agent
    """
    os = detect_OS(http_user_agent)
    browser = detect_browser(http_user_agent)
    simplified = OS_OTHER

    if os != OS_OTHER and browser != BROWSER_OTHER:

        # For each key check what is it
        for k, v in OS_DETAILED.items():
            #If is the same then nothing more to search
            if k == os:
                simplified = k
                break
            else:
                # now check if the detailed OS is one in the detailed OS list
                # of the simplified OS
                # We asume that the check data is lowercase
                if os.lower() in v:
                    simplified = k  # The key is the simplified OS
                    break

    return (simplified, browser, os)


def detect_country_location_with_geoip(ip):
    """extracts the location from an IP. This is possible with the MaxMind DB
    so, the database is needed: http://www.maxmind.com/download/geoip/database/
    And the GeoIP C lib: http://www.maxmind.com/download/geoip/api/c/
    Returns a dict with "country_code" and "country_name"

    :param ip: The ip for extracting the location
    """

    g = GeoIP()
    return g.country(ip)
