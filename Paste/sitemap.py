from django.contrib.sitemaps import Sitemap
from Paste.models import Paste
from ratelimit.mixins import RatelimitMixin


class PasteSitemap(RatelimitMixin, Sitemap):
    ratelimit_key = 'ip'
    ratelimit_rate = '20/s'
    ratelimit_block = True
    ratelimit_method = 'GET'

    changefreq = 'daily'
    priority = 0.9

    def items(self):
        return Paste.objects.filter(is_public=True)

    def lastmod(self, obj):
        return obj.publish

    def location(self, obj):
        return obj.slug
