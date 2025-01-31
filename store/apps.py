from django.apps import AppConfig


class StoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'store'

    def ready(self):
        from .signals import handlers
        return super().ready()


   # the ready method is called when the store app starts