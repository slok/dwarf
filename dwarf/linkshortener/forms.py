from django import forms
from django.utils.translation import ugettext_lazy as _


class ShortUrlForm(forms.Form):
    url = forms.URLField(label=_(u'URL'))