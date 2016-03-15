from django.apps import AppConfig

__author__ = 'paulguichon'

class DuckPayZenConfig(AppConfig):
    name = 'duck_inscription_payzen'
    verbose_name = 'Duck Inscription Payzen'

    def ready(self):
        from django.conf.urls import url, include
        import duck_inscription_payzen.signals
        self.urls = [
            url(r'^paiement_payzen/', include("duck_inscription_payzen.urls")),
        ]