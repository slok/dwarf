from datetime import datetime

from django.shortcuts import (render_to_response, RequestContext)

from metrics.models import LoginMetrics
from dwarfutils.dateutils import datetime_now_utc
from dwarfutils.googlechartutils import day_metrics_linechart_json_transform


def day_logins(request):
    now = datetime_now_utc()
    today = datetime(year=now.year, month=int(now.month), day=now.day)
    yesterday = datetime(year=now.year, month=int(now.month), day=now.day - 1)
    two_days_ago = datetime(year=now.year, month=int(now.month), day=now.day - 2)
    three_days_ago = datetime(year=now.year, month=int(now.month), day=now.day - 3)
    four_days_ago = datetime(year=now.year, month=int(now.month), day=now.day - 4)
    five_days_ago = datetime(year=now.year, month=int(now.month), day=now.day - 5)

    results_today = (today.strftime("%Y-%m-%d"),
                     LoginMetrics(today).count_hours_logins())
    results_yesterday = (yesterday.strftime("%Y-%m-%d"),
                         LoginMetrics(yesterday).count_hours_logins())
    results_two_days = (two_days_ago.strftime("%Y-%m-%d"),
                        LoginMetrics(two_days_ago).count_hours_logins())
    results_three_days = (three_days_ago.strftime("%Y-%m-%d"),
                          LoginMetrics(three_days_ago).count_hours_logins())
    results_four_days = (four_days_ago.strftime("%Y-%m-%d"),
                         LoginMetrics(four_days_ago).count_hours_logins())
    results_five_days = (five_days_ago.strftime("%Y-%m-%d"),
                         LoginMetrics(five_days_ago).count_hours_logins())

    data = day_metrics_linechart_json_transform(results_today,
                                                results_yesterday,
                                                results_two_days,
                                                results_three_days,
                                                results_four_days,
                                                results_five_days,
                                                )
    context = {
        "data": data,
    }

    return render_to_response('metrics/daylogins.html',
                              context,
                              context_instance=RequestContext(request))
