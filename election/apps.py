from django.apps import AppConfig

class ElectionAppConfig(AppConfig):
    name = 'election'

    def ready(self):
        import election.signals
