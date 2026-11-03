"""
Test-only settings override.

Inherits everything from config.settings but replaces the PostgreSQL
database with an in-memory SQLite database so that the test suite can
run in local development without a running PostgreSQL server.

Usage:
    python backend/manage.py test accounts employees \
        --settings=config.test_settings
"""

from .settings import *  # noqa: F401, F403

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}
