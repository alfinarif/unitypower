# Performance and background work

Billing reconciliation runs as one database-backed task instead of inside a page
request. Run a Django task worker as a separate long-lived process:

```text
python manage.py db_worker
```

Relevant billing pages enqueue reconciliation when no billing task is already
queued or running. Schedule `python manage.py billing_task_runner` periodically
to refresh billing even when those pages are not visited. Page responses no
longer wait for reconciliation, so updated balances may appear after the task
finishes.

The daily WhatsApp scheduler also runs separately, rather than starting in each
web process. If that broadcast is enabled, run it as its own long-lived process:

```text
python manage.py run_whatsapp_scheduler
```
