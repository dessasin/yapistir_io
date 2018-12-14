from django.contrib import admin
from django import forms
from .models import Paste, Report, Contact


class PasteAdminForm(forms.ModelForm):
    class Meta:
        model = Paste
        fields = '__all__'


class ReportAdminForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = '__all__'


class ContactAdminForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = '__all__'


class PasteAdmin(admin.ModelAdmin):
    form = PasteAdminForm
    list_display = ['slug', 'publish', 'expire', 'view_count']
    readonly_fields = ['slug', 'publish', 'expire', 'view_count']
    search_fields = [
        'slug'
    ]


class ReportAdmin(admin.ModelAdmin):
    form = ReportAdminForm
    list_display = ['slugs_id', 'mail', 'reason', 'rapor_nedeni']
    readonly_fields = ['slugs_id', 'mail', 'reason', 'rapor_nedeni']
    search_fields = [
        'slugs_id'
    ]


class ContactAdmin(admin.ModelAdmin):
    form = ContactAdminForm
    list_display = ['ad_soyad', 'iletisim_nedeni', 'mail', 'aciklama']
    readonly_fields = ['ad_soyad', 'iletisim_nedeni', 'mail', 'aciklama']
    search_fields = [
        'ad_soyad'
    ]


admin.site.register(Paste, PasteAdmin)
admin.site.register(Report, ReportAdmin)
admin.site.register(Contact, ContactAdmin)
