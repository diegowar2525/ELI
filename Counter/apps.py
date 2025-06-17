from django.apps import AppConfig


class CounterConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Counter'

    def ready(self):
        print("Se cargaron los signals de Counter")
        import Counter.signals  # Asegúrate de que el nombre coincida
