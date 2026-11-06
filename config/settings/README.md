# Django settings

- `config.settings.development` is the local default used by `manage.py`. It
  loads the ignored project-root `.env` file and enables debug mode by default.
- `config.settings.deployment` is the default for ASGI and WSGI. It does not
  load `.env`; provide configuration through the process environment or a
  deployment secret manager.
- `config.settings.base` contains settings shared between both environments.

Copy `.env.example` to `.env` for development. Never commit `.env`, Firebase
credentials, or production secrets. Generate a Django key with:

```text
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Set `DJANGO_SECRET_KEY` and `DJANGO_ALLOWED_HOSTS` in deployment. The default
database is SQLite at `db.sqlite3`, as requested; provide a persistent,
backed-up volume for that file in deployment. `DATABASE_ENGINE` and the
`DATABASE_*` variables can be used to configure PostgreSQL later, but changing
database engines requires a separate data migration.

Configure Firebase push notifications with a service-account JSON file via
`GOOGLE_APPLICATION_CREDENTIALS`, or enable
`FIREBASE_USE_APPLICATION_DEFAULT_CREDENTIALS=true` when the deployment provides
Google Application Default Credentials. Messaging credentials should be
supplied through environment variables, not source files.

Before deploying, run migrations and collect static assets:

```text
python manage.py migrate --settings=config.settings.deployment
python manage.py collectstatic --noinput --settings=config.settings.deployment
python manage.py check --deploy --settings=config.settings.deployment
```

HTTPS redirect and secure cookies are enabled by deployment settings. Set
`DJANGO_TRUST_PROXY_SSL_HEADER=true` only when a trusted reverse proxy removes
client-supplied forwarding headers and sets `X-Forwarded-Proto`. HSTS is
enabled for one year by default. Confirm HTTPS works for every configured
hostname before deployment; `DJANGO_SECURE_HSTS_SECONDS=0` temporarily disables
it during initial TLS setup.
