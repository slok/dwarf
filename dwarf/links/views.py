import logging
import math

from django.shortcuts import render_to_response, RequestContext
from django.http import Http404
from django.contrib.auth.decorators import login_required

from linkshortener.models import UserLink, ShortLink
from dwarfutils.dateutils import unix_to_datetime, datetime_now_utc
from clickmanager.models import Click
from dwarfutils.googlechartutils import (pie_chart_json_transform,
                                    single_linechart_json_transform_with_list)

logger = logging.getLogger("dwarf")

LINK_PER_PAGE = 10


@login_required
def links_index(request):

    # get the page
    page = int(request.GET.get('page', 1))

    # Get the total pages (rounding up, ex: 1.2 pages means 2 pages)
    total_pages = int(math.ceil(
                        float(UserLink.objects.filter(
                                user=request.user).count()) / LINK_PER_PAGE))

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

    return render_to_response('links/user_links.html',
                              context,
                              context_instance=RequestContext(request))


@login_required
def links_info(request, token):

    sl = ShortLink.find(token=token)

    clicks = Click.findall(token)

    # get browsers:
    browsers = {}
    os = {}
    languages = {}
    countries = {}
    dates_tmp = {}
    dates = []
    date_format = "Date({0}, {1}, {2})"

    for i in clicks:

        # Browsers
        try:
            browsers[i.browser] += 1
        except KeyError:
            browsers[i.browser] = 1

        # Operative Systems
        try:
            os[i.os] += 1
        except KeyError:
            os[i.os] = 1

        # Languages (Browser)
        try:
            languages[i.language] += 1
        except KeyError:
            languages[i.language] = 1

        # Countries

        try:
            countries[i.location] += 1
        except KeyError:
            countries[i.location] = 1

        # dates
        dt = unix_to_datetime(i.click_date)
        dt_str = date_format.format(dt.year, dt.month-1, dt.day)
        try:
            dates_tmp[dt_str] += 1
        except KeyError:
            dates_tmp[dt_str] = 1

    # Fill the dates until now
    from dateutil.relativedelta import relativedelta
    now = datetime_now_utc() + relativedelta(months=1)
    temp_date = unix_to_datetime(sl.creation_date)

    while (temp_date.day != now.day or
            temp_date.month != now.month or
            temp_date.year != now.year):

        dt_str = date_format.format(temp_date.year,
                                    temp_date.month-1,
                                    temp_date.day)
        try:
            dates.append((dt_str, dates_tmp[dt_str]))
        except KeyError:
            import random
            dates.append((dt_str, random.randrange(5, 10)))
            #dates.append((dt_str, 0))

        temp_date += relativedelta(days=1)

    context = {
        'browser_data': pie_chart_json_transform("Browsers", browsers),
        'os_data': pie_chart_json_transform("Operative systems", os),
        'languages_data': pie_chart_json_transform("Languages", languages),
        'countries_data': pie_chart_json_transform("Countries", countries),
        'dates_data': single_linechart_json_transform_with_list("Clicks", "Days", dates),
        'short_link': sl
    }

    return render_to_response('links/link_info.html',
                              context,
                              context_instance=RequestContext(request))