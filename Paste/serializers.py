from Paste.models import Paste
from rest_framework import serializers
import uuid
import hashlib
from django.utils import timezone
from random import SystemRandom

from Paste import highlight

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


class PasteSerializer(serializers.Serializer):
    content = serializers.CharField()
    name = serializers.CharField(max_length=40, allow_null=True)
    publish = serializers.DateTimeField()
    lexer = serializers.CharField(max_length=60, default='_text')
    expire = serializers.DateTimeField(allow_null=True)
    expire_type = serializers.IntegerField()
    slug = serializers.CharField(max_length=255)
    auth_code = serializers.CharField(max_length=32)
    view_count = serializers.IntegerField(default=0)
    url_change_count = serializers.IntegerField(default=0)
    ip_adress = serializers.IPAddressField()
    is_public = serializers.BooleanField(default=True)
    password = serializers.CharField(allow_null=True)

    class Meta:
        model = Paste
        fields = '__all__'

    def create(self, validated_data):
        if self.view_count:
            pass
        else:
            expire = self.expire
            self.expire, self.expire_type = get_expire(expire)
            self.publish = timezone.localtime()
            self.slug = generate_secret_id()
            self.auth_code = hashlib.md5(str(uuid.uuid4()).encode('UTF-8')).hexdigest()
            self.content = self.content
            self.is_public = self.is_public
            self.password = self.password
        super(PasteSerializer, self).create(**validated_data)
