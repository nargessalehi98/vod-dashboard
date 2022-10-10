from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from admin_control.views import (
    add_admin,
    edit_admin,
    get_admins,
    get_access_list,
    add_access_group,
    get_access_groups,
    edit_access_groups,
    add_provider,
    edit_provider,
    get_providers,
    delete_provider,
    get_persons,
    get_genres,
    add_tag,
    get_tag,
    get_serials

)
from config.logger import log_error

urls = {
    'addAdmin': add_admin,
    'editAdmin': edit_admin,
    'getAdmins': get_admins,

    'getAccessList': get_access_list,
    'addAccessGroup': add_access_group,
    'getAccessGroups': get_access_groups,
    'editAccessGroups': edit_access_groups,

    'addProvider': add_provider,
    'editProvider': edit_provider,
    'getProviders': get_providers,
    'deleteProvider': delete_provider,

    'getPersons': get_persons,
    'getGenres': get_genres,
    'addTag': add_tag,
    'getTag': get_tag,

    'getSerials': get_serials,
}


@api_view(http_method_names=['POST'])
def admin_routing(request, *args, **kwargs):
    # return urls[request.api_method](request, *args, **kwargs)
    if request.api_method not in urls.keys():
        return not_found(request, *args, **kwargs)
    try:
        return urls[request.api_method](request, *args, **kwargs)
    except Exception as e:
        log_error(e, request=request)
        return Response(status=status.HTTP_409_CONFLICT)


def not_found(request, *args, **kwargs):
    log_error('URL not found', request=request)
    return Response(status=status.HTTP_404_NOT_FOUND)
