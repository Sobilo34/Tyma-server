#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    # Check for different deployment environments
    if 'PIXL_SPACE' in os.environ or 'PIXL_HOSTNAME' in os.environ:
        settings_module = 'core.pixl_settings'
    elif 'RENDER_EXTERNAL_HOSTNAME' in os.environ:
        settings_module = 'core.deployment_settings'
    else:
        settings_module = 'core.settings'
    
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_module)
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
