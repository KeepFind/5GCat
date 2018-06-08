from django.apps import AppConfig


class AdvanceConfig(AppConfig):
    name = 'advance'

    def ready(self):
        import manage.signals
