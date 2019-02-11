#!/usr/bin/env python
import os
import sys

map_environment = {
    'prod': 'production',
    'dev': 'local',
    'staging': 'staging'
}

if __name__ == '__main__':
    try:
        environment = map_environment[os.environ.get('ENVIRONMENT')]
    except KeyError:
        raise ValueError('ENVIRONMENT variable "{}" unknown. Choose dev, prod or staging !'.format(environment))

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'YOUR_PROJECT.settings.{}'.format(environment))
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)
