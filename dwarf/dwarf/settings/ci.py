import os

from dev import *

DEBUG = True
SECRET_KEY = 'FaKe KeY'

# Get geoip data path
GEOIP_PATH = os.getenv("GEOIP_PATH")
if not GEOIP_PATH:
    GEOIP_PATH = "/var/lib/geoip"
