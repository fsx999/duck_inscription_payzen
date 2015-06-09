from django.apps import AppConfig

__author__ = 'paulguichon'

class DuckPayZenConfig(AppConfig):
    name = 'duck_inscription_payzen'
    verbose_name = 'Duck Inscription Payzen'

    def ready(self):
        import duck_inscription_payzen.signals