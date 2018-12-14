from django.conf import settings
from django.core.management.base import BaseCommand
from elasticsearch_dsl import Index
from elasticsearch.helpers import bulk
from elasticsearch import Elasticsearch
from Paste.models import Paste
from Paste.doc_type import PasteDoc


class Command(BaseCommand):
    help = 'Elastic Search Indexes'

    def handle(self, *args, **options):
        es = Elasticsearch(
            [{'host': settings.ES_HOST, 'port': settings.ES_PORT}],
            index="paste"
        )
        skill_index = Index('paste')
        skill_index.doc_type(PasteDoc)
        if skill_index.exists():
            skill_index.delete()
            print('Indis temizlendi')
            PasteDoc.init()
        result = bulk(
            client=es,
            actions=(paste.indexing() for paste in Paste.objects.all().iterator())
        )
        print('Işlem başarılı')
        print(result)
