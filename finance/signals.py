# your_app/signals.py
from django.db.backends.signals import connection_created
from django.dispatch import receiver


@receiver(connection_created)
def enable_sqlite_wal(sender, connection, **kwargs):
  if connection.vendor == 'sqlite':
    cursor = connection.cursor()
    cursor.execute('PRAGMA journal_mode=WAL;')
    cursor.execute('PRAGMA synchronous=NORMAL;')  # Recommended pairing with WAL
    cursor.execute(
        'PRAGMA busy_timeout=5000;'
    )  # Avoids immediate 'database is locked' errors
