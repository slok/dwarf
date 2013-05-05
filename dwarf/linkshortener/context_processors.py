from linkshortener.forms import ShortUrlForm


def link_shortener_form_context_processor(request):
    form = ShortUrlForm()
    return {
        'link_shortener_form': form
    }
