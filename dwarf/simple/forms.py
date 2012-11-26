from django import forms
from django.core.validators import URLValidator


class URLForm(forms.Form):
    url = forms.CharField(max_length=40,
                        label=u'URL',
                        validators=[URLValidator])
