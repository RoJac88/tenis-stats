from flask import url_for


def get_next_prev_links(route, page, result_set, LIMIT, parameters={}):
    if page > 1:
        previous = url_for(route, page=page - 1, **parameters)
    else:
        previous = None
    if len(result_set) >= LIMIT:
        _next = url_for(route, page=page + 1, **parameters)
    else:
        _next = None
    return previous, _next
