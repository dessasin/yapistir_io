from django.contrib.auth import logout
from django.contrib import messages
from django.utils.deprecation import MiddlewareMixin
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
from Paste.models import Visitor
from django.utils.cache import add_never_cache_headers
from TPaste import settings
from Paste.utils import get_client_ip
from django.utils import timezone


class SessionIdleTimeout(MiddlewareMixin):
    warning_message = 'Oturumunuzun Süresi Doldu'

    def process_request(self, request):
        if request.user.is_authenticated():
            current_datetime = timezone.datetime.now()
            if 'last_login' in request.session:
                last = (current_datetime - request.session['last_login']).seconds
                if last > settings.SESSION_IDLE_TIMEOUT:
                    logout(request)
                    messages.add_message(request, messages.WARNING, self.warning_message)
            else:
                request.session['last_login'] = current_datetime
        return None


class OneSessionPerUserMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if isinstance(request.user, User):
            current_key = request.session.session_key
            if hasattr(request.user, 'visitor'):
                active_key = request.user.visitor.session_key
                if active_key != current_key:
                    Session.objects.filter(session_key=active_key).delete()
                    request.user.visitor.session_key = current_key
                    request.user.visitor.save()
            else:
                Visitor.objects.create(
                    user=request.user,
                    session_key=current_key,
                )


class LogVariablesMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user:
            user = request.user
        else:
            user = 'anonymous'
        request.log_extra = {
            'client_ip': get_client_ip(request),
            'user': user
        }


class DoNotTrackMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if 'HTTP_DNT' in request.META:
            if request.META['HTTP_DNT'] == '1':
                request.dnt = True
            else:
                request.dnt = False
        else:
            request.dnt = None

    def process_response(self, request, response):
        if 'HTTP_DNT' in request.META:
            response['DNT'] = request.META['HTTP_DNT']
        return response


class DisableClientSideCachingMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        add_never_cache_headers(response)
        return response
