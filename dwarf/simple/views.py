import json

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

    clicks = list(Click.findall(token=token))
    # Sort
    clicks.sort(key=lambda click: click.click_id)
    
    short_link = ShortLink.find(token=token)

    # Get data for the charts
    browsers = get_data_for_charts(clicks, "browser")
    browsers.append("Browsers")
    os = get_data_for_charts(clicks, "os")
    os.append("OS")
    country = get_data_for_charts(clicks, "location")
    country.append("Country")

    not_json_data = (browsers, os, country)

    #Serialize
    json_data = json.dumps(not_json_data)

    data = {
        'shortlink': short_link,
        'clicks': clicks,
        'json_data': json_data
    }

    return render_to_response('simple/details.html',
                            data,
                            context_instance=RequestContext(request))


def get_data_for_charts(clicks, param):
    """ Returns a tuple with (titles, counts) of a given parameter to extract
    from the click inforamtion
    """

    my_list_aux = [getattr(i, param, "Unknown") for i in clicks]
    my_list = []
    for i in my_list_aux:
        x = "Unknown" if not i else i
        my_list.append(x)
    titles = set(my_list)
    counts = [my_list.count(i) for i in titles]
    return [list(titles), counts]
