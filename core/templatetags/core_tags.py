from django import template


register = template.Library()


@register.filter
def split_pipe(value):
    if not value:
        return []

    return [item for item in str(value).split("|") if item]
