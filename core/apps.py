from django.apps import AppConfig

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    verbose_name = 'E-RECYCLO Core'
    
    def ready(self):
        # Import signals if we create them later
        # import core.signals
        pass