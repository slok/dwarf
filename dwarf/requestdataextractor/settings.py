
from django.conf import settings


#Important!!! all lower case

# Some OS and browser need to be checked before others for example Android is
# also Linux, so Android needs to be checked before Linux.
# In browsers for example Chrome also is safari

OS_ANDROID = ("android",)
OS_LINUX = ("linux i686", "linux x86_64", "linux")
OS_BSD = ("Freebsd", "Openbsd", "netbsd", "bsd")
OS_IOS = ("ios", "iphone", "ipad", "ipod")
OS_MAC = ("macintosh", "mac")
OS_WINDOWS = ("windows nt 5.1", "windows nt 6.1", "windows",)
OS_BLACKBERRY = ("rim", "blackberry")
OS_STEAM = ("steam",)
OS_GAME_CONSOLE = ("xbox", "playstation", "wiiu", "wii", "nintendo ds")


def get_os_detailed():
    OS_DETAILED = {
        'android': OS_ANDROID,
        'linux': OS_LINUX,
        'bsd': OS_BSD,
        'ios': OS_IOS,
        'mac': OS_MAC,
        'windows': OS_WINDOWS,
        'blackberry': OS_BLACKBERRY,
        'console': OS_GAME_CONSOLE,
    }

    return OS_DETAILED


def get_os_catalog():
    OS_CATALOG = OS_ANDROID + OS_LINUX + OS_BSD + OS_IOS + OS_MAC +\
                OS_WINDOWS + OS_BLACKBERRY + OS_STEAM + OS_GAME_CONSOLE
    return OS_CATALOG


def get_browser_catalog():
    BROWSER_CATALOG = ("seamonkey", "konqueror", "chrome",
        "opera", "steam", "firefox", "safari", "ie")
    return BROWSER_CATALOG

OS_OTHER = getattr(settings, 'OS_OTHER', "other")
BROWSER_OTHER = OS_OTHER
OS_CATALOG = getattr(settings, 'OS_CATALOG', get_os_catalog())
BROWSER_CATALOG = getattr(settings, 'BROWSER_CATALOG',
                                get_browser_catalog())
OS_DETAILED = getattr(settings, 'OS_DETAILED', get_os_detailed())
