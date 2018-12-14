from django.db.models.signals import post_save
from django.dispatch import receiver

from Paste.models import Paste
from Paste.doc_type import PasteDoc


@receiver(post_save, sender=Paste)
def my_handler(sender, instance, **kwargs):
    instance.indexing()
