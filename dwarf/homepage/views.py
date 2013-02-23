from django.shortcuts import (render_to_response,
                             RequestContext, redirect)


def index(request):
     return render_to_response('homepage/index.html',
                            context_instance=RequestContext(request))