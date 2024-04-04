from django import template

register = template.Library()

@register.simple_tag
def querystring_replace(request, key, value):
    """Replace the given `key` with the given `value`
    in the request's querystring. The rest of the
    querystring remains unchanged.
    """
    query_dict = request.GET.copy()
    query_dict[key] = value
    print(query_dict.urlencode())
    return f'?{query_dict.urlencode()}'
