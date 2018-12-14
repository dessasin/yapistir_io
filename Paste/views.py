from django.views.generic import FormView
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView, DeleteView
from django.views import View
from django.contrib import messages
from django.urls import reverse
from Paste.models import Paste, Report, Contact, PasteUser, get_expire, Tags, TagLists
from Paste.forms import (
    PasteForm,
    PasteUpdateForm,
    ProtectedDatailViewForm,
    ReportForm,
    ContactForm
)
from django.conf import settings
from django.http import Http404, HttpResponseRedirect, HttpResponse, HttpResponseForbidden
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from Paste.PasteCrawl import is_pasebin_url, get_pastebin_content
import sys
import requests
from ratelimit.mixins import RatelimitMixin
from .utils import get_client_ip
from Paste import forms
from allauth.account.forms import AddEmailForm
from allauth.account.views import ChangePasswordForm
from rest_framework.authtoken.models import Token
# ---------------------------------------------------
# ---------------------REST API----------------------
# ---------------------------------------------------
from Paste.serializers import PasteSerializer
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.throttling import UserRateThrottle
from rest_framework import permissions, renderers
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from Paste.doc_type import PasteDoc


def check_recaptcha(self):
    data = {
        'secret': settings.RECAPTCHA_PRIVATE_KEY,
        'response': self.request.POST.get('g-recaptcha-response')
    }
    r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
    result = r.json()
    if result['success'] or self.request.user.is_authenticated():
        return True
    else:
        return False


# Create your views here.
class IndexView(FormView):
    model = Paste
    form_class = PasteForm
    slug_url_kwarg = 'paste_id'
    slug_field = 'paste_id'
    template_name = 'pages/index.html'
    error_message = _(u'Kayıt sırasında bir sorun oluştu')
    error_message_content = _(u'İçerik Alanı Zorunludur.')

    def get_context_data(self, **kwargs):
        public_pastes = super(IndexView, self).get_context_data(**kwargs)
        public_pastes.update({
            'publics': Paste.objects.filter(is_public=True, password='').exclude(password__isnull=True).order_by('-id')[:7],
        })
        return public_pastes

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        if check_recaptcha(self):

            if sys.getsizeof(form.cleaned_data['content']) <= 512000:  # 512kb Limit

                if get_pastebin_content(is_pasebin_url(form.cleaned_data['content'])):  # Pastebin Check
                    c = get_pastebin_content(is_pasebin_url(form.cleaned_data['content']))
                else:
                    c = form.cleaned_data['content']
                if self.request.user.is_authenticated():
                    self.post_content = Paste(content=c,
                                              title=form.cleaned_data['title'],
                                              name=self.request.user.username,
                                              lexer=form.cleaned_data['lexer'],
                                              expire=form.cleaned_data['expire'],
                                              ip_adress=get_client_ip(self.request),
                                              is_public=form.cleaned_data['status'],
                                              password=form.cleaned_data['password'])
                    self.post_content.save()
                    self.paste_user = PasteUser(user_id_id=self.request.user.pk,
                                                paste_id_id=self.post_content.pk)
                    self.paste_user.save()
                    for item in form.cleaned_data['tags'].replace('+', '').split(','):
                        try:
                            tag = Tags.objects.get(word=item)
                            tag_id = tag.id
                        except:
                            self.tag_contet = Tags(word=item)
                            self.tag_contet.save()
                            tag_id = self.tag_contet.pk

                        self.tag_list = TagLists(pasteid_id=self.post_content.pk,
                                                 tagid_id=tag_id)
                        self.tag_list.save()

                    obj = PasteDoc(
                        meta={'id': self.post_content.pk},
                        title=form.cleaned_data['title'],
                        slug=self.post_content.slug,
                        tag=form.cleaned_data['tags'].replace('+', '')
                    )
                    obj.save()
                else:
                    self.post_content = Paste(content=c,
                                              title=form.cleaned_data['title'],
                                              name='Anonim',
                                              lexer=form.cleaned_data['lexer'],
                                              expire=form.cleaned_data['expire'],
                                              ip_adress=get_client_ip(self.request),
                                              is_public=form.cleaned_data['status'],
                                              password=form.cleaned_data['password'])
                    self.post_content.save()
                    for item in form.cleaned_data['tags'].replace('+', '').split(','):

                        try:
                            tag = Tags.objects.get(word=item)
                            tag_id = tag.id
                        except:
                            self.tag_contet = Tags(word=item)
                            self.tag_contet.save()
                            tag_id = self.tag_contet.pk

                        self.tag_list = TagLists(pasteid_id=self.post_content.pk,
                                                 tagid_id=tag_id)
                        self.tag_list.save()
                    obj = PasteDoc(
                        meta={'id': self.post_content.pk},
                        title=form.cleaned_data['title'],
                        slug=self.post_content.slug,
                        tag=form.cleaned_data['tags'].replace('+', '')
                    )
                    obj.save()
                return super(IndexView, self).form_valid(form)
            else:
                messages.error(self.request, 'Maximum 512kb girebilirsiniz.')
                return HttpResponseRedirect(reverse('paste_new'))
        else:
            messages.error(self.request, 'reCAPTCHA doğrulaması başarısız')
            return HttpResponseRedirect(reverse('paste_new'))

    def form_invalid(self, form):
        messages.add_message(self.request, messages.ERROR, self.error_message)
        return super(IndexView, self).form_invalid(form)

    def get_success_url(self):
        return reverse('paste_details', kwargs={'paste_id': self.post_content.slug})


class DetailPasteView(DetailView, FormView):
    model = Paste
    form_class = ProtectedDatailViewForm
    slug_url_kwarg = 'paste_id'
    slug_field = 'slug'
    template_name = 'pages/paste_details.html'

    def get(self, *args, **kwargs):
        paste = self.get_object()

        paste.view_count += 1
        paste.save(update_fields=['view_count'])

        if paste.password:
            return HttpResponseRedirect(reverse('protect', kwargs={'paste_id': self.kwargs['paste_id']}))
        else:
            return super(DetailPasteView, self).get(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        paste = self.get_object()
        form = ProtectedDatailViewForm(self.request.POST)
        if form.is_valid():
            if paste.password == form.cleaned_data['password']:
                paste.view_count += 1
                paste.save(update_fields=['view_count'])
                return super(DetailPasteView, self).get(*args, request, **kwargs)
            else:
                messages.error(request, 'Geçersiz Parola')
                return reverse('paste_details', kwargs={'paste_id': self.kwargs['paste_id']})
        else:
            return HttpResponseRedirect(reverse('protect', kwargs={'paste_id': self.kwargs['paste_id']}))

    def get_initial(self):
        snippet = self.get_object()
        return {'content': snippet.content, 'lexer': snippet.lexer, 'lines': snippet.get_linecount()}

    def get_context_data(self, **kwargs):
        ctx = super(DetailPasteView, self).get_context_data(**kwargs)
        kimlik = Paste.objects.get(slug=self.kwargs['paste_id']).id
        ctx.update(
            {
                'tags': Tags.objects.filter(taglists__pasteid_id=kimlik),
                'wordwrap': self.object.lexer in forms.LEXER_WORDWRAP,
            }
        )
        return ctx


class ProtectedView(DetailView, FormView):
    model = Paste
    form_class = ProtectedDatailViewForm
    slug_url_kwarg = 'paste_id'
    slug_field = 'slug'
    template_name = 'registration/protected.html'

    def get(self, *args, **kwargs):
        paste = self.get_object()
        if paste.password:
            return super(ProtectedView, self).get(*args, **kwargs)
        else:
            raise Http404


class DetailPasteRawView(DetailView):
    """
    Yapıştırılan içeriğin ham hali gösterilecektir.
    """
    model = Paste
    slug_url_kwarg = 'paste_id'
    slug_field = 'slug'
    template_name = 'pages/paste_details_raw.html'

    def render_to_response(self, context, **response_kwargs):
        snippet = self.get_object()
        if snippet.password:
            return HttpResponseForbidden('Protected')
        decode_snippet = snippet.content
        response = HttpResponse(decode_snippet)
        response['Content-Type'] = 'text/plain;charset=UTF-8'
        response['X-Content-Type-Options'] = 'nosniff'
        return response


"""
class DetailPasteEmbedView(DetailView):
    model = Paste
    slug_url_kwarg = 'paste_id'
    slug_field = 'slug'
    template_name = 'include/embeds.html'

    def get(self, *args, **kwargs):
        snippet = self.get_object()

        if snippet.password:
            return HttpResponseForbidden('Protected')
        return super(DetailPasteEmbedView, self).get(*args, **kwargs)
"""


class AboutView(TemplateView):
    template_name = 'pages/about.html'

    def get_context_data(self, **kwargs):
        statistics = super(AboutView, self).get_context_data(**kwargs)
        statistics.update({
            'total': Paste.objects.count()
        })
        return statistics


class ProfileContainerView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        paste = PasteUser.objects.filter(user_id_id=request.user.pk).values_list('paste_id_id', flat=True)
        pastes = Paste.objects.filter(pk__in=paste).order_by('-publish')
        paginator = Paginator(pastes, 15)
        page = request.GET.get('page', 1)
        try:
            pastes = paginator.page(page)
        except PageNotAnInteger:
            pastes = paginator.page(1)
        except EmptyPage:
            pastes = paginator.page(paginator.num_pages)

        data = {
            'pastes_list': pastes,
            'total': Paste.objects.count(),
            'paste_total': PasteUser.objects.filter(user_id_id=self.request.user.pk).count()
        }
        return render(request, 'pages/profile/links.html', data)


class ProfileDetailsView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        try:
            user_token = Token.objects.get(user_id=request.user.pk)
        except:
            user_token = Token.objects.create(user_id=request.user.pk)
        data = {
            'password_change': ChangePasswordForm,
            'add_mail': AddEmailForm,
            'user_token': user_token.key
        }
        return render(request, 'pages/profile/profile_details.html', data)


class UserPasteChangeView(LoginRequiredMixin, UpdateView):
    def get(self, request, *args, **kwargs):
        content = Paste.objects.get(auth_code=self.kwargs['auth_id'])
        form = PasteUpdateForm(initial={
            'lexer': content.lexer,
            'expire': content.expire,
            'content': content.content,
        })
        data = {
            'form': form
        }
        return render(request, 'pages/profile/change.html', data)

    def post(self, request, *args, **kwargs):
        form = PasteUpdateForm(request.POST)
        if form.is_valid():
            self.paste = Paste.objects.filter(auth_code=self.kwargs['auth_id']).update(
                lexer=form.cleaned_data['lexer'],
                expire=get_expire(form.cleaned_data['expire']),
                content=form.cleaned_data['content'],
                ip_adress=get_client_ip(self.request)
            )
            self.paste.save()
            messages.success(request, 'İçerik Güncellendi')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        else:
            messages.success(request, 'Bilinmeyen HATA')
            return HttpResponseRedirect(reverse('linkler'))


class DeletedView(LoginRequiredMixin, DeleteView):
    model = Paste

    def get(self, request, *args, **kwargs):
        auth_code = self.kwargs['auth_id']
        pastes = Paste.objects.get(auth_code=auth_code)
        pastes.delete()
        messages.success(request, 'Başarıyla Silindi')
        return HttpResponseRedirect(reverse('linkler'))


class PrivacyView(TemplateView):
    template_name = 'pages/privacy.html'


class DisclaimerView(TemplateView):
    template_name = 'pages/disclaimer.html'


class TermsView(TemplateView):
    template_name = 'pages/terms_of_service.html'


class ContentSearchView(RatelimitMixin, ListView):
    ratelimit_key = 'ip'
    ratelimit_rate = '1/s'
    ratelimit_block = False
    ratelimit_method = 'GET'

    model = Paste
    paginate_by = 10
    template_name = 'pages/search.html'

    def get_queryset(self):
        from Paste.doc_type import PasteDoc
        result = super(ContentSearchView, self).get_queryset()

        query = self.request.GET.get('q')
        if query:
            result = PasteDoc.search().query("multi_match", query=query, fields=['title', 'tag'], type="phrase_prefix")[
                     :30]
        return result


class ReportView(FormView):
    model = Report
    form_class = ReportForm
    template_name = 'pages/report_area.html'

    def post(self, request, *args, **kwargs):
        form = ReportForm(request.POST)
        if form.is_valid():
            self.report = Report(slugs_id=form.cleaned_data['slugs_id'],
                                 mail=form.cleaned_data['mail'],
                                 reason=form.cleaned_data['reason'],
                                 rapor_nedeni=form.cleaned_data['rapor_nedeni'])
            self.report.save()
            messages.success(self.request, 'Teşekkürler. Kötüye kullanım bildiriminiz gerçekleştirilmiştir.')
            return HttpResponseRedirect(reverse('paste_report_view'))
        else:
            messages.error(self.request, "Kötüye kullanım bildiriminiz gönderilemedi")
            return HttpResponseRedirect(reverse('paste_report_view'))


class ContactView(FormView):
    model = Contact
    form_class = ContactForm
    template_name = 'pages/contact_form.html'

    def post(self, request, *args, **kwargs):
        form = ContactForm(request.POST)
        if form.is_valid():
            self.contacts = Contact(ad_soyad=form.cleaned_data['ad_soyad'],
                                    iletisim_nedeni=form.cleaned_data['iletisim_nedeni'],
                                    mail=form.cleaned_data['mail'],
                                    aciklama=form.cleaned_data['aciklama'])
            self.contacts.save()
            messages.success(self.request,
                             'İletişime geçtiğiniz için teşekkür ederiz, en kısa sürede geri dönüş yapılacaktır.')
            return HttpResponseRedirect(reverse('contact_view'))
        else:
            messages.error(self.request, "İletişim Mesajınız Gönderilemedi")
            return HttpResponseRedirect(reverse('contact_view'))


# ---------------------------------------------------
# ---------------------------------------------------
"""class ApiLoginView(RatelimitMixin, APIView):
    ratelimit_key = 'ip'
    ratelimit_rate = '3/s'
    ratelimit_block = True
    ratelimit_method = 'POST'

    renderer_classes = [renderers.JSONRenderer]
    permission_classes = (permissions.AllowAny,)

    @method_decorator(csrf_exempt)
    def post(self, request, *args, **kwargs):
        username = request.data.get("username")
        password = request.data.get("password")
        if username is None or password is None:
            return Response({'error': 'Lütfen kullanıcı adınızı ve parolanızı giriniz'},
                            status=status.HTTP_400_BAD_REQUEST)
        user = authenticate(username=username, password=password)
        if not user:
            return Response({'error': 'Geçersiz'},
                            status=status.HTTP_404_NOT_FOUND)
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key},
                        status=status.HTTP_200_OK)


class PasteSerializerCreate(RatelimitMixin, APIView):
    ratelimit_key = 'ip'
    ratelimit_rate = '1/s'
    ratelimit_block = False
    ratelimit_method = 'POST'

    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    throttle_classes = (UserRateThrottle,)

    def get(self, request, *args, **kwargs):
        content = {
            'status': 'request was permitted'
        }
        return Response(content)

    @method_decorator(csrf_exempt)
    def post(self, request, *args, **kwargs):
        serializer = PasteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)"""
