from django.shortcuts import (render_to_response,
                             RequestContext)
from django.http import Http404
from django.contrib import messages

from simple.forms import URLForm
from linkshortener.tasks import create_token
from linkshortener.models import ShortLink
from linkshortener.exceptions import ShortLinkNotFoundError
from clickmanager.models import Click


def index(request):

    if request.method == 'POST':
        form = URLForm(request.POST)
        if form.is_valid():
            try:
                result = create_token.delay(form.cleaned_data['url'])
                token = result.get()
                messages.success(request, 'New token {0} created'.format(token))
            except:
                raise Http404

    form = URLForm()

    # Get links
    try:
        links = ShortLink.findall()
        total_links = ShortLink.get_counter()
    except ShortLinkNotFoundError:
        total_links = 0
        links = ()

    data = {
        'my_form': form,
        'total_links': total_links,
        'links': links
    }

    return render_to_response('simple/index.html',
                            data,
                            context_instance=RequestContext(request))


def details(request, token):
    print("Hello {0}".format(token))
    data = {
        'shortlink': ShortLink.find(token=token),
        'clicks': Click.findall(token=token)
    }

    return render_to_response('simple/details.html',
                            data,
                            context_instance=RequestContext(request))
