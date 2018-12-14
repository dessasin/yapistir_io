from django.utils import timezone
from django.conf import settings
from django.contrib.auth import logout
from django.contrib.sessions.models import Session
from django.core.management.base import BaseCommand
from django.http import HttpRequest
from importlib import import_module

def session_process(session_key):
    engine = import_module(settings.SESSION_ENGINE)
    return engine.SessionStore(session_key)


class Command(BaseCommand):
    help = "Aktif oturumlarin hepsini kapat"
    
    def handle(self, *args, **options):
        """
        Tüm oturumların okunması ve zamana dayalı olarak tüm oturumlardan çıkılmasını sağlamaktadır.
        """
        start = timezone.now() - timezone.timedelta(days=1)
        request = HttpRequest()
     
        sessions = Session.objects.filter(expire_date__gt=start)
     
        print('Tespit Edilen %d Adet Oturum Hala Acik' % len(sessions))
     
        for session in sessions:
            username = session.get_decoded().get('_auth_user_id')
            request.session = session_process(session.session_key)
            logout(request)
            print('Kapatilan Oturumlar %r ' % username)
        print('Tamamlandi!')
