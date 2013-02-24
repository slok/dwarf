from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist


class SignupForm(forms.Form):
    username = forms.CharField(label=_(u'username'))
    password1 = forms.CharField(label=_(u"password"),
                                widget=forms.PasswordInput)
    password2 = forms.CharField(label=_(u"Repeat password"),
                                widget=forms.PasswordInput)
    email = forms.EmailField(label=_(u'email'))

    def clean_username(self):
        """Checks if the suer exists"""
        try:
            username = self.cleaned_data.get('username')
            User.objects.get(username=username)
        except ObjectDoesNotExist:
            return username

        # If no exception then wrong user
        raise forms.ValidationError(_(u"This username is already taken"))

    def clean_password2(self):
        """Checks if both passwords are the same"""
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if not password2:
            raise forms.ValidationError(_(u"You must confirm your password"))
        if password1 != password2:
            raise forms.ValidationError(_(u"Your passwords do not match"))
        return password2

    def clean_email(self):
        """Checks if the email exists"""
        try:
            email = self.cleaned_data.get('email')
            User.objects.get(email=email)
        except ObjectDoesNotExist:
            return email

        # If no exception then wrong email
        raise forms.ValidationError(_(u"This email is already taken"))


class ResetPasswordForm(forms.Form):
    email = forms.EmailField(label=_(u'email'))

    def clean_email(self):
        """Checks if the email exists"""
        try:
            email = self.cleaned_data.get('email')
            User.objects.get(email=email)
            return email
        except ObjectDoesNotExist:
            raise forms.ValidationError(_(u"This email doesn't exists"))
