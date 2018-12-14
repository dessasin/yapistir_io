import uuid
import hashlib

from pygments import lexers
from random import SystemRandom
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User
from django.contrib.sitemaps import ping_google
from Paste.highlight import pygmentize
from Paste.doc_type import PasteDoc

R = SystemRandom()


def generate_secret_id(length=None, tries=0):
    length = 4
    alphabet = 'abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNOPQRSTUVWXYZ1234567890'
    slug = ''.join([R.choice(alphabet) for i in range(length)])
    try:
        Paste.objects.get(slug=slug)
    except Paste.DoesNotExist:
        return slug
    return generate_secret_id(length=length + 1, tries=tries)


def get_expire(expire):
    if expire == 'never':
        expire_type = 2
        expire = None
    elif expire == '30d':
        expire_type = 3
        expire = timezone.localtime() + timezone.timedelta(days=30)
    elif expire == '7d':
        expire_type = 3
        expire = timezone.localtime() + timezone.timedelta(days=7)
    elif expire == '1h':
        expire_type = 3
        expire = timezone.localtime() + timezone.timedelta(hours=1)
    else:
        expire_type = 2
        expire = None
    return expire, expire_type


# Create your models here.
class Paste(models.Model):
    content = models.TextField()
    highlighted = models.TextField(blank=True)
    title = models.CharField(max_length=160, blank=True, db_index=True)
    name = models.CharField(max_length=40, blank=True)
    publish = models.DateTimeField()
    lexer = models.CharField(max_length=60, default='_code')
    expire = models.DateTimeField(blank=True, null=True)
    expire_type = models.PositiveSmallIntegerField()
    slug = models.SlugField(max_length=255, unique=True, db_index=True)
    auth_code = models.CharField(max_length=32, db_index=True)
    view_count = models.IntegerField(default=0)
    ip_adress = models.GenericIPAddressField()
    is_public = models.BooleanField(default=True)
    password = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        ordering = ('-view_count',)
        db_table = 'Paste'
        managed = True
        verbose_name = 'Paste'
        verbose_name_plural = 'Yapıştırılanlar'

    def __str__(self):
        return self.slug

    def get_linecount(self):
        return len(self.content.splitlines())

    def highlight(self):
        return pygmentize(self.content, self.lexer)

    def save(self, *args, **kwargs):
        if self.view_count:
            pass
        else:
            expire = self.expire
            self.title = self.title
            self.expire, self.expire_type = get_expire(expire)
            self.publish = timezone.localtime()
            self.slug = generate_secret_id()
            self.auth_code = hashlib.md5(str(uuid.uuid4()).encode('UTF-8')).hexdigest()
            self.content = self.content
            self.highlighted = self.highlight()
            self.is_public = self.is_public
            self.password = self.password
        super(Paste, self).save(*args, **kwargs)
        try:
            ping_google()
        except Exception:
            pass

    def indexing(self):
        pass
        obj = PasteDoc(
            meta={'id': self.id},
            title=self.title,
            slug=self.slug,
        )
        obj.save()
        return obj.to_dict(include_meta=True)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('Paste.views.DetailPasteView', args=[str(self.slug)])


class Report(models.Model):
    slugs_id = models.SlugField()
    mail = models.EmailField()
    reason = models.CharField(max_length=255, default='spammer')
    rapor_nedeni = models.TextField()

    class Meta:
        db_table = 'Report'
        managed = True
        verbose_name = 'Report'

    def __str__(self):
        return self.mail


class Contact(models.Model):
    ad_soyad = models.CharField(max_length=160)
    iletisim_nedeni = models.CharField(max_length=60)
    mail = models.EmailField()
    aciklama = models.TextField()

    class Meta:
        db_table = 'Contact'
        managed = True
        verbose_name = 'Contact'

    def __str__(self):
        return self.ad_soyad


class Tags(models.Model):
    word = models.CharField(max_length=35, db_index=True)
    slug = models.CharField(max_length=250)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'Tags'
        managed = True
        verbose_name = 'Tags'

    def __str__(self):
        return self.word


class TagLists(models.Model):
    pasteid = models.ForeignKey(Paste, on_delete=models.CASCADE)
    tagid = models.ForeignKey(Tags, on_delete=models.CASCADE)

    def __str__(self):
        return "%s | %s" % (str(self.pasteid), str(self.tagid))

    class Meta:
        db_table = 'TagLists'
        managed = True
        verbose_name = 'TagLists'


class PasteUser(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    paste_id = models.ForeignKey(Paste, on_delete=models.CASCADE)

    class Meta:
        db_table = 'PasteUser'
        managed = True
        verbose_name = 'PasteUser'


class Visitor(models.Model):
    user = models.OneToOneField(User)
    session_key = models.CharField(max_length=40, null=True, blank=True)

    class Meta:
        db_table = 'Visitor'
        managed = True
        verbose_name = 'Visitor'


class Language(models.Model):
    name = models.CharField(max_length=100)
    lang_code = models.CharField(max_length=100, unique=True, verbose_name='Vurgulama')
    slug = models.SlugField(max_length=100, unique=True)
    mime = models.CharField(max_length=100, help_text='Snippeti dosya olarak gönderirken kullanılacak MIME.')
    file_extension = models.CharField(max_length=10)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def get_lexer(self):
        return lexers.get_lexer_by_name(self.lang_code)

    def __str__(self):
        return self.name


def get_default_language():
    lang = Language.objects.get_or_create(
        name='Plain Text',
        lang_code='text',
        slug='text',
        mime='text/plain',
        file_extension='.txt',
    )

    return lang[0].id
