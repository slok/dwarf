from django.shortcuts import (render_to_response,
                             RequestContext, redirect)
#from django.http import Http404
from django.contrib import messages
from django.contrib.auth.models import User

from userprofile.models import Profile
from userprofile.forms import SignupForm


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
