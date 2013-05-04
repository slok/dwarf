import json
import logging

from django.shortcuts import (render_to_response,
                             RequestContext, redirect)
from django.http import HttpResponse, Http404
from django.contrib import messages
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required

from linkshortener.forms import ShortUrlForm
from linkshortener.tasks import create_token

logger = logging.getLogger("dwarf")


def create_link_helper(url, user_id):

    result = create_token.delay(url, user_id)
    token = result.get()
    logger.debug("Creating a short link... '{0}' token".format(token))

    return token


@login_required
def create_link(request):
    if request.method == 'POST':
        form = ShortUrlForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            # Get user
            user_id = request.user.id
            token = create_link_helper(data['url'], user_id)
            messages.success(request, "Your link Has been created: {0}".format(token))
    else:
        form = ShortUrlForm()

    context = {
        'form': form,
    }

    return render_to_response('linkshortener/create_link.html',
                            context,
                            context_instance=RequestContext(request))

#def ajax_create_link(request):
#    """Ajax view that checks if the user exists. If the username is already
#    registered then returs True if not False
#    """
#    response_data = {
#        'token': None,
#        'message': None
#    }
#    response = create_link()
#    #try:
#    #    User.objects.get(username=username)
#    #    response_data['error'] = unicode(_(u"This username is already taken"))
#    #except ObjectDoesNotExist:
#    #    response_data['exists'] = False
#
#    return HttpResponse(json.dumps(response_data), mimetype="application/json")