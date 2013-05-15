from django import forms


class DeleteLinkForm(forms.Form):
    token = forms.CharField(widget=forms.HiddenInput())


class DisableLinkForm(forms.Form):
    token = forms.CharField(widget=forms.HiddenInput())
