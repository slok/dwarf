from celery import task

from clickmanager.models import Click
from requestdataextractor.extractors import detect_browser_and_OS


@task()
def click_link(token, request_meta_dict):

    #Extract data
    user_agent = request_meta_dict.get('HTTP_USER_AGENT')
    data = detect_browser_and_OS(user_agent)
    ip = request_meta_dict.get('REMOTE_ADDR')
    language = request_meta_dict.get('LANG')

    #TODO: location, remote host

    c = Click(token=token, browser=data[1], os=data[2], ip=ip,
            language=language)

    c.save()
