from django.shortcuts import (render_to_response,
                             RequestContext)
from django.http import Http404

from simple.forms import URLForm
from linkshortener.tasks import create_token


def index(request):

    if request.method == 'POST':
        form = URLForm(request.POST)
        if form.is_valid():
            try:
                result = create_token.delay(form.cleaned_data['url'])
                token = result.get()
            except:
                raise Http404
            return render_to_response('simple/shortened.html',
                            {'shortened_link': token},
                            context_instance=RequestContext(request))
    else:
        form = URLForm()

    data = {
        'my_form': form,
    }

    return render_to_response('simple/index.html',
                            data,
                            context_instance=RequestContext(request))
