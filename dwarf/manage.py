#!/usr/bin/env python
import os
import sys

# The settings filenames without ".py" extension
SETTINGS = {
    'production': "prod",
    'development': "dev",
    'continous_integration': "ci",
}

if __name__ == "__main__":

    # Settings import format
    settings_location = "dwarf.settings.{0}"

    # Check wich is the environment for the settings
    if os.getenv('CI') == "true" or os.getenv('TRAVIS') == "true":
        active_settings = SETTINGS['continous_integration']
    elif os.getenv('PRODUCTION') == "true":
        active_settings = SETTINGS['production']
    else:
        active_settings = SETTINGS['development']

    # Load settings
    os.environ.setdefault("DJANGO_SETTINGS_MODULE",
                        settings_location.format(active_settings))

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
