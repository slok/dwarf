

def current_url_context_processor(request):
    return {
        "current_url": request.get_full_path()
    }
