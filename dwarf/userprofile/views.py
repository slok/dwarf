from django.shortcuts import (render_to_response,
                             RequestContext, redirect)
from django.http import Http404
from django.contrib import messages

from userprofile.models import Profile


def activate_account(request, user_id, token):

    user = Profile.objects.get(id=user_id)

    if not user or user.activation_token != token:
        messages.error(request, "Account activation failed")
    else:
        messages.success(request, "Account activated!")
        user.activated = True
        user.save()

    return redirect("/")

def password_reset(request, user, token):
    pass
