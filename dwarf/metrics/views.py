import json
from datetime import datetime

from django.shortcuts import (render_to_response, RequestContext)

from metrics.models import LoginMetrics
from dwarfutils.dateutils import datetime_now_utc


def day_logins(request):
    now = datetime_now_utc()
    today = datetime(year=now.year, month=int(now.month), day=now.day)
    yesterday = datetime(year=now.year, month=int(now.month), day=now.day - 1)
    two_days_ago = datetime(year=now.year, month=int(now.month), day=now.day - 2)

    results_today = LoginMetrics(today).count_hours_logins()
    results_yesterday = LoginMetrics(yesterday).count_hours_logins()
    results_two_days = LoginMetrics(two_days_ago).count_hours_logins()
    data = {
        "cols": [
            {"id": "hour", "label": "Hour", "type": "string"},
            {"id": "total", "label": "Total Logins " + today.strftime("%Y-%m-%d"), "type": "number"},
            {"id": "total", "label": "Total Logins " + yesterday.strftime("%Y-%m-%d"), "type": "number"},
            {"id": "total", "label": "Total Logins " + two_days_ago.strftime("%Y-%m-%d"), "type": "number"},
        ],
        "rows": []
    }

    for i in range(24):
        value_today = results_today[i]
        value_yesterday = results_yesterday[i]
        value_two_days = results_two_days[i]
        single_data = {
            "c": [{"v": '{0}:00'.format(i)},
                  {"v": value_today},
                  {"v": value_yesterday},
                  {"v": value_two_days}
                  ]
        }
        data['rows'].append(single_data)
    print(json.dumps(data))
    context = {
        "data": json.dumps(data),
    }

    return render_to_response('metrics/daylogins.html',
                              context,
                              context_instance=RequestContext(request))
