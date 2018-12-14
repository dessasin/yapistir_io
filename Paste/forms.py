from django import forms
from django.core.validators import RegexValidator
from Paste.highlight import LEXER_CHOICES
from django.forms.widgets import TextInput, Textarea, Select
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from snowpenguin.django.recaptcha2.fields import ReCaptchaField
from snowpenguin.django.recaptcha2.widgets import ReCaptchaWidget
from snowpenguin.django.recaptcha2.widgets import ReCaptchaHiddenInput

from allauth.account.forms import (
    SignupForm,
    LoginForm,
    ResetPasswordForm,
)

CONTACT_CHOICES = (
    ('telif_ihlali', _('Güvenlik İhlali')),
    ('oneri', _('Öneri')),
    ('soru', _('Soru')),
    ('diger', _('Diğer'))
)

REASON_CHOICES = (
    ('gizlilik_ihlali', _('Gizlilik İhlali')),
    ('hak_ihlali', _('Haklarımı ihlal ediyor')),
    ('child_abuse', _('Çocuk istismarı')),
    ('terorism', _('Terörizmi teşvik ediyor')),
    ('spammer', _('Spam veya yanıltıcı içerik')),
    ('danger_content', _('Zarar verici tehlikeli hareketler')),
    ('nefret_soylemi', _('Nefret söylemi veya aşağılayıcı dil')),
    ('ataturke_abuse', _('Atatürk aleyhine işlenen suçlar')),
    ('uyusturucu_abuse', _('Uyuşturucu veya uyarıcı madde kullanılmasını kolaylaştırma')),
    ('intihar_abuse', _('İntihara yönlendirme')),
)

EXPIRE_CHOICES = (
    ('1h', _('Bir saat içinde yok et')),
    ('7d', _('Bir hafta içinde yok et')),
    ('30d', _('Bir ay içinde yok et')),
    ('never', _('Asla yok etme')),
)

PUBLIC_CHOICES = (
    (1, _('Genele Açık Paylaş')),
    (0, _('Paylaşma')),
)

EXPIRE_DEFAULT = 'never'
REASON_DEFAULT = 'spammer'
CONTACT_DEFAULT = 'soru'

LEXER_DEFAULT = '_code'
PUBLIC_DEFAULT = 1
LEXER_WORDWRAP = ('rst',)

"""
    yapıştırma içerik form alanı
"""


class PasteForm(forms.Form):
    status = forms.ChoiceField(
        choices=PUBLIC_CHOICES,
        initial=PUBLIC_DEFAULT,
        widget=Select(attrs={'class': 'input'}),
    )

    lexer = forms.ChoiceField(
        choices=LEXER_CHOICES,
        initial=LEXER_DEFAULT,
        widget=Select(attrs={'class': 'input'}),
    )

    expire = forms.ChoiceField(
        choices=EXPIRE_CHOICES,
        initial=EXPIRE_DEFAULT,
        widget=Select(attrs={'class': 'input'}),
    )

    title = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={'class': 'input', 'autocomplete': 'off',
                   'placeholder': 'İçeriğiniz için başlık girebilirsiniz'}),
    )

    content = forms.CharField(
        widget=Textarea(
            attrs={'class': 'textarea', 'rows': '10', 'maxlength': '262144000',
                   'placeholder': 'Yapıştırılacak içerik buraya gelecek...'}),
        required=True,
    )

    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'input', 'placeholder': 'parola ile içerik koruma'}),
    )

    tags = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={'class': 'input'}),
        validators=[RegexValidator('[a-zA-Z0-9]+', message='Sadece Alphanumeric', code='invalid_tags')]
    )

    def clean(self):
        cleaned_data = super(PasteForm, self).clean()
        title = cleaned_data.get('title')
        content = cleaned_data.get('content')
        tags = cleaned_data.get('tags')
        if len(title) > 160:
            raise ValidationError("Maximum 160 karakter girebilirsiniz.")
        if not content:
            raise ValidationError("İçerik girişi yapmalısınız.")
        if not tags:
            raise ValidationError("Etiket girişi yapmalısınız.")


"""
    içerik guncelleme form alanı
"""


class PasteUpdateForm(forms.Form):
    lexer = forms.ChoiceField(
        choices=LEXER_CHOICES,
        initial=LEXER_DEFAULT,
        widget=Select(attrs={'class': 'input'}),
    )

    expire = forms.ChoiceField(
        choices=EXPIRE_CHOICES,
        initial=EXPIRE_DEFAULT,
        widget=Select(attrs={'class': 'input'})
    )

    content = forms.CharField(
        widget=Textarea(
            attrs={'class': 'textarea', 'rows': '20', 'placeholder': 'Yapıştırılacak içerik buraya gelecek...'}),
        label=_(u'İçerik'),
        required=True,
    )


"""
    parola korumalı yapıştırmalardaki form yapısı
"""


class ProtectedDatailViewForm(forms.Form):
    captcha = ReCaptchaField(widget=ReCaptchaWidget())
    password = forms.CharField(
        label=_(u'Parola'),
        required=True,
        widget=forms.PasswordInput(attrs={'minlength': '4'}),
    )

    def clean(self):
        cleaned_data = super(ProtectedDatailViewForm, self).clean()
        password = cleaned_data.get('password')
        if len(password) < 4:
            raise ValidationError("Minimum 4 karakter girebilirsiniz.")
        if not password:
            raise ValidationError("Parola Girmelisiniz.")


"""
    Kötüye kullanım bildirme alanı form yapımız
"""


class ReportForm(forms.Form):
    rapor_nedeni = forms.CharField(
        widget=Textarea(
            attrs={'class': 'textarea', 'rows': '10', 'minlength': '40',
                   'placeholder': 'Kötüye kullanım bildirme nedeniniz'}),
        required=True,
    )

    reason = forms.ChoiceField(
        choices=REASON_CHOICES,
        initial=REASON_DEFAULT,
        widget=Select(attrs={'class': 'input'}),
        required=True,
    )

    mail = forms.CharField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'input', 'placeholder': 'Mail adresiniz'}),
    )

    slugs_id = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'input'}),
    )

    captcha = ReCaptchaField(widget=ReCaptchaWidget())


"""
    İletişim formunda kullanılacak yapı
"""


class ContactForm(forms.Form):
    ad_soyad = forms.CharField(
        widget=TextInput(
            attrs={'class': 'input', 'maxlength': '160',
                   'placeholder': 'Adınız ve Soyadınız'}),
        required=True,
    )

    iletisim_nedeni = forms.ChoiceField(
        choices=CONTACT_CHOICES,
        initial=CONTACT_DEFAULT,
        widget=Select(attrs={'class': 'input'}),
    )

    mail = forms.CharField(
        widget=forms.EmailInput(attrs={'class': 'input', 'placeholder': 'Mail adresiniz'}),
        required=True,
    )

    aciklama = forms.CharField(
        widget=Textarea(
            attrs={'class': 'textarea', 'rows': '10', 'minlength': '10',
                   'placeholder': 'Mesajınız'}),
        required=True,
    )

    captcha = ReCaptchaField(widget=ReCaptchaWidget())


# ---------------------------------------------
# Recaptcha
# ---------------------------------------------

class MyCustomLoginForm(LoginForm):
    captcha = ReCaptchaField(widget=ReCaptchaWidget())


class MyCustomSignupForm(SignupForm):
    captcha = ReCaptchaField(widget=ReCaptchaWidget())


class MyCustomResetPasswordForm(ResetPasswordForm):
    captcha = ReCaptchaField(widget=ReCaptchaWidget())
