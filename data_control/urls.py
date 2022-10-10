from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from config.logger import log_error
from data_control.views import (
    get_all_contents,
    edit_content,
    get_most_visited_content,
    get_total_traffic,
    get_content_access_count,
)

urls = {
    'getContentsManagement': get_all_contents,
    'getContents': get_all_contents,
    'editContent': edit_content,
    'getMostVisitedContent': get_most_visited_content,
    'getTotalTraffic': get_total_traffic,
    'getSpecificTraffic': get_total_traffic,
    'getContentSegmentAccessCount': get_content_access_count,
}


@api_view(http_method_names=['POST'])
def data_routing(request, *args, **kwargs):
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
