import json


def day_metrics_linechart_json_transform(*args):
    """Converts the day metrics to the json for googlecharts.
    Receives  tuple arguments (title, list_of_values) where the list of values
    is a list of values
    """
    data = {
        "cols": [{"id": "hour", "label": "Hour", "type": "string"}, ],
        "rows": []
    }

    for i in args:
        data['cols'].append({"id": "total", "label": i[0], "type": "number"})

    for j in range(24):
        single_data = {"c": [{"v": '{0}:00'.format(j)}, ]}
        for k in args:
            single_data['c'].append({"v": k[1][j]})
        data['rows'].append(single_data)

    return json.dumps(data)
