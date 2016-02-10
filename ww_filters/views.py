from django.shortcuts import HttpResponse, get_object_or_404, redirect
from django.conf import settings

from . import models


def check_filter_form_valid(filter_, data):
    filter_params = {}
    str_dct = data['data'][1:].split('&')
    for param in str_dct:
        param_data = param.split('=')
        filter_params[param_data[0]] = param_data[1]
    filter_collection = filter_[0](filter_[1].objects.none(), filter_params)
    filter_collection.update_qs()
    return any(f.error for f in filter_collection.filters.values())


def save_filter(request):
    data = request.GET
    if check_filter_form_valid(settings.FILTERS_BY_TYPE.get(data['type']), data):
        return HttpResponse('error')
    else:
        models.SavedFilters.objects.create(name=data['name'], data=data['data'], user_id=data['user'], 
                                           source=data['source'], type=data['type'])
        return HttpResponse('ok')


def delete_filter(request, pk):
    saved_filter = get_object_or_404(models.SavedFilters, pk=pk)
    src = saved_filter.source
    saved_filter.delete()
    return redirect(src)
