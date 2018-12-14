from django import template
from django.conf import settings
from django.utils.safestring import mark_safe
import sys
from django.http import Http404
from Paste.highlight import pygmentize

register = template.Library()


@register.simple_tag
def recaptcha(needs_autoescape=True):
    return mark_safe(
        """<script src='https://www.google.com/recaptcha/api.js'></script><div class="g-recaptcha" data-sitekey="{0}"></div>""".format(
            settings.RECAPTCHA_PUBLIC_KEY))


@register.filter
def filesize(value):
    return sys.getsizeof(value)


@register.filter
def in_list(value, arg):
    return value in arg


@register.filter
def highlight(object):
    try:
        h = object.highlighted
        h = h.replace(u'  ', u'&nbsp;&nbsp;')
        h = h.replace(u'\t', '&nbsp;&nbsp;&nbsp;&nbsp;') # tab = 4 space
        return h.splitlines()
    except:
        raise Http404()
