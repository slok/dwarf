from django import forms
from django.utils.translation import ugettext_lazy as _


class ShortUrlForm(forms.Form):
    url = forms.URLField(
            label=_(u'URL'),
            widget=forms.TextInput(attrs={
                                    'placeholder': _(u'Short your Link!'),
                                    'style': "width:220%",
                                   }))
