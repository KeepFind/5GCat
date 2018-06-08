from django.apps import AppConfig


class ManageConfig(AppConfig):
    name = 'manage'

    def ready(self):
        import manage.signals
