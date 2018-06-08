from django.apps import AppConfig


class AdConfig(AppConfig):
    name = 'ad'

    def ready(self):
        import manage.signals
