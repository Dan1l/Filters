from django import template

register = template.Library()


@register.inclusion_tag('ww_filters/_list_forms.html', takes_context=True)
def ww_filters(context, type_):
    context['type'] = type_
    return context
