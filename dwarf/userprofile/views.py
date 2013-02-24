import json
import logging

from django.shortcuts import (render_to_response,
                             RequestContext, redirect)
from django.http import HttpResponse, Http404
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.views import login

from userprofile.models import Profile
from userprofile.forms import SignupForm


logger = logging.getLogger("dwarf")


def signup(request):

    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user = User()
            user.username = data['username']
            user.set_password(data['password1'])
            user.email = data['email']
            user.save()

            # Send email
            messages.success(request,
                    "You are now part of the crew. Please confirm your account before login in")
    else:
        form = SignupForm()

    context = {
        'form': form,
    }

    return render_to_response('userprofile/signup.html',
                            context,
                            context_instance=RequestContext(request))


def ajax_username_exists(request, username):
    """Ajax view that checks if the user exists. If the username is already
    registered then returs True if not False
    """
    logger.debug("Checking ajax call for the username existence")

    response_data = {'exists': True}
    try:
        User.objects.get(username=username)
        response_data['error'] = unicode(_(u"This username is already taken"))
    except ObjectDoesNotExist:
        response_data['exists'] = False

    return HttpResponse(json.dumps(response_data), mimetype="application/json")


def ajax_email_exists(request):
    """Ajax view that checks if the user exists. If the username is already
    registered then returs True if not False
    """
    logger.debug("Checking ajax call for the email existence")

    if request.method == 'POST':
        response_data = {'exists': True}
        try:
            email = request.POST['email']
            if not email:
                raise Http404

            User.objects.get(email=email)

            response_data['error'] = unicode(_(u"This email is already taken"))
        except ObjectDoesNotExist:
            response_data['exists'] = False

        return HttpResponse(json.dumps(response_data),
            mimetype="application/json")

    else:
        raise Http404


def activate_account(request, user_id, token):

    user = Profile.objects.get(id=user_id)

    if not user or user.activation_token != token:
        messages.error(request, "Account activation failed")
    else:
        messages.success(request, "Account activated!")
        user.activated = True
        user.save()

    return redirect("/")


def custom_login(request, template_name):
    if request.user.is_authenticated():
        #TODO: Change!
        return redirect("/works")

    else:
        return login(request, template_name)


def password_reset(request, user, token):
    pass
