from django.apps import AppConfig


class MembershipConfig(AppConfig):
    name = 'membership'

    def ready(self):
        import finance.signals
