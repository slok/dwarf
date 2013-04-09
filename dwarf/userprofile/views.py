import json
import logging
import math

from django.shortcuts import (render_to_response,
                             RequestContext, redirect)
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _
#from django.contrib.auth.views import login
from django.utils import timezone
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import REDIRECT_FIELD_NAME, login as auth_login
from django.utils.http import is_safe_url
from django.shortcuts import resolve_url
from django.conf import settings
from django.contrib.sites.models import get_current_site
from django.template.response import TemplateResponse

from userprofile.models import Profile
from userprofile.forms import SignupForm, ResetPasswordForm
from linkshortener.models import UserLink, ShortLink
from dwarfutils.hashutils import get_random_hash
from dwarfutils.dateutils import unix_to_datetime
from metrics.models import LoginMetrics
from achievements.signals.signals import user_signup

logger = logging.getLogger("dwarf")

LINK_PER_PAGE = 10


################################################################################
# Copied code from Django (Need to put code in between, like metrics and stuff)
@sensitive_post_parameters()
@csrf_protect
@never_cache
def custom_login(request, template_name='registration/login.html',
                 redirect_field_name=REDIRECT_FIELD_NAME,
                 authentication_form=AuthenticationForm,
                 current_app=None, extra_context=None):
    """
    Displays the login form and handles the login action.
    """

    # If the user is already authenticated not need to login
    if request.user.is_authenticated():
        messages.info(request, _(u"You are already logged in"))
        # Redis login metrics
        LoginMetrics().save_user_login(request.user.id)
        return redirect(reverse(user_dashboard))

    redirect_to = request.REQUEST.get(redirect_field_name, '')

    if request.method == "POST":
        form = authentication_form(data=request.POST)
        if form.is_valid():

            # Ensure the user-originating redirection url is safe.
            if not is_safe_url(url=redirect_to, host=request.get_host()):
                redirect_to = resolve_url(settings.LOGIN_REDIRECT_URL)

            # Okay, security check complete. Log the user in.
            auth_login(request, form.get_user())

            if request.session.test_cookie_worked():
                request.session.delete_test_cookie()

            # Everything ok. Start our custom code
            # Redis login metrics
            LoginMetrics().save_user_login(request.user.id)

            return HttpResponseRedirect(redirect_to)
    else:
        form = authentication_form(request)

    request.session.set_test_cookie()

    current_site = get_current_site(request)

    context = {
        'form': form,
        redirect_field_name: redirect_to,
        'site': current_site,
        'site_name': current_site.name,
    }
    if extra_context is not None:
        context.update(extra_context)
    return TemplateResponse(request, template_name, context,
                            current_app=current_app)


#def custom_login(request, template_name):
#    if request.user.is_authenticated():
#        messages.info(request, _(u"You are already logged in"))
#        print(messages)
#        return redirect(reverse(user_dashboard))
#
#    else:
#        return login(request, template_name)
################################################################################

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

            # Send signal
            if settings.ENABLE_ACHIEVEMENTS:
                user_signup.send(sender=user)

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


@login_required
def user_dashboard(request):

    # get the page
    page = int(request.GET.get('page', 1))

    # Get the total pages (rounding up, ex: 1.2 pages means 2 pages)
    total_pages = int(math.ceil(float(UserLink.objects.count()) / LINK_PER_PAGE))

    # If the page doesn't exists then 404
    if page > total_pages and total_pages > 0:
        raise Http404

    # Get the links
    offset = LINK_PER_PAGE * (page - 1)
    limit = offset + LINK_PER_PAGE
    links_aux = UserLink.objects.filter(user=request.user).order_by('-id')[offset:limit]
    links = [ShortLink.find(token=i.token) for i in links_aux]

    # Group by day
    grouped_links = []
    temp = []

    for i in links:
        creation_date = unix_to_datetime(i.creation_date)

        if len(temp) == 0:
            temp.append(i)
        else:
            previous_date = unix_to_datetime(temp[0].creation_date)
            if previous_date.year == creation_date.year and\
                previous_date.month == creation_date.month and\
                previous_date.day == creation_date.day:
                temp.append(i)
            else:
                grouped_links.append(temp)
                temp = []
    # If no links don't add them
    if temp:
        grouped_links.append(temp)

    context = {
        "total_pages": total_pages,
        "actual_page": page,
        "links": grouped_links
    }

    return render_to_response('userprofile/dashboard.html',
                        context,
                        context_instance=RequestContext(request))


def reset_password(request, user, token):
    pass


def ask_reset_password(request):
    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user = User.objects.get(email=data['email'])
            profile = Profile.objects.get(user=user)

            # Set hash and date
            profile.password_reset_token = get_random_hash()
            profile.password_reset_token_date = timezone.now()
            profile.save()

            logger.debug("Reset password in: " +\
                reverse(reset_password, args=[user.id, profile.password_reset_token]))

            # Send email
            messages.success(request, "An email has been sent to your account")
    else:
        form = ResetPasswordForm()

    context = {
        'form': form,
    }

    return render_to_response('userprofile/reset-password.html',
                            context,
                            context_instance=RequestContext(request))
