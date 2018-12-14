"""TPaste URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""

from django.conf.urls import url, include
from django.contrib import admin
from django.conf import settings
from django.views.generic import TemplateView
from Paste.views import (
    DetailPasteView,
    DetailPasteRawView,
    # DetailPasteEmbedView,
    AboutView,
    ProfileContainerView,
    IndexView,
    DeletedView,
    PrivacyView,
    ProtectedView,
    DisclaimerView,
    # ApiLoginView,
    UserPasteChangeView,
    # PasteSerializerCreate,
    ContentSearchView,
    ReportView,
    TermsView,
    ProfileDetailsView,
    ContactView
)
from allauth.account.views import (
    PasswordChangeView,
    EmailView,
)

from django.contrib.sitemaps.views import sitemap
from Paste.sitemap import PasteSitemap

sitemaps = {
    'static': PasteSitemap,
}

L = getattr(settings, 'SLUG_LENGTH', 4)

urlpatterns = [

    # Main
    # ---------------------------------------------------
    # ---------------------------------------------------
    url(r'^{}/'.format(settings.ADMIN_URL), admin.site.urls),
    url(r'^$', IndexView.as_view(), name='paste_new'),
    url(r'^About/$', AboutView.as_view(), name='about'),
    url(r'^Privacy/$', PrivacyView.as_view(), name='privacy'),
    url(r'^terms_of_service/$', TermsView.as_view(), name='terms_of_service'),
    url(r'^Disclaimer/$', DisclaimerView.as_view(), name='disclaimer'),

    # Sitemap
    # ---------------------------------------------------
    # ---------------------------------------------------
    url(r'^sitemap\.xml$', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),

    # REST Api User Logic
    # ---------------------------------------------------
    # ---------------------------------------------------
    # url(r'^Api/v1/Login/$', ApiLoginView.as_view(), name='rest_login'),
    # url(r'^Api/v1/New/$', PasteSerializerCreate.as_view(), name='paste_api_create_new'),

    # Static Areas
    # ---------------------------------------------------
    # ---------------------------------------------------
    url(r'^ChangeLog/$', TemplateView.as_view(template_name="changelog.txt", content_type="text/plain"), name='changelog'),
    url(r'^robots.txt$', TemplateView.as_view(template_name="robots.txt", content_type="text/plain"), name="robots_file"),
    url(r'^License/$', TemplateView.as_view(template_name="license.txt", content_type="text/plain"), name="license_file"),

    # Social Login Partial
    # ---------------------------------------------------
    # ---------------------------------------------------
    url(r'^accounts/', include('allauth.urls')),

    # Email
    # ---------------------------------------------------
    # ---------------------------------------------------
    url(r"^email/$", EmailView.as_view(template_name="pages/profile/profile_details.html", success_url='/accounts/profile/'), name="account_email"),
    url(r"^password/change/$", PasswordChangeView.as_view(template_name='pages/profile/profile_details.html', success_url='/accounts/profile/'),name="account_change_password"),

    # Other Function Areas
    # ---------------------------------------------------
    # ---------------------------------------------------
    url(r'^Search', ContentSearchView.as_view(), name='search'),
    url(r'^Report', ReportView.as_view(), name='paste_report_view'),
    url(r'^Contact', ContactView.as_view(), name='contact_view'),
    url(r'^accounts/container/$', ProfileContainerView.as_view(), name='linkler'),
    url(r'^accounts/profile/$', ProfileDetailsView.as_view(), name='profil_details_view'),

    # Functions
    # ---------------------------------------------------
    # ---------------------------------------------------
    url(r'^(?P<auth_id>[a-fA-F0-9]{32})/Delete/$', DeletedView.as_view(), name='sil'),
    url(r'^(?P<auth_id>[a-fA-F0-9]{32})/Change/$', UserPasteChangeView.as_view(), name='degistir'),

    # Show Pastes
    # ---------------------------------------------------
    # ---------------------------------------------------
    url(r'^(?P<paste_id>[a-zA-Z0-9]{%d,})/Protected/' % L, ProtectedView.as_view(), name='protect'),
    url(r'^(?P<paste_id>[a-zA-Z0-9]{%d,})/$' % L, DetailPasteView.as_view(), name='paste_details'),
    url(r'^(?P<paste_id>[a-zA-Z0-9]{%d,})/Raw/$' % L, DetailPasteRawView.as_view(), name='paste_details_raw'),
    #url(r'^Embeded/(?P<paste_id>[a-zA-Z0-9]{%d,})' % L, DetailPasteEmbedView.as_view(), name='paste_details_embed'),
]
