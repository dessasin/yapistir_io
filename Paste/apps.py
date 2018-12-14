from django.apps import AppConfig
from elasticsearch_dsl import connections
from django.conf import settings

class PasteConfig(AppConfig):
    name = 'Paste'
    verbose_name = 'Paste'

    def ready(self):
        import Paste.signals
        try:
            connections.create_connection(hosts=[{'host': settings.ES_HOST, 'port': settings.ES_PORT}])
        except Exception as e:
            print(e)
