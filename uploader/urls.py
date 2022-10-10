from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from config.logger import log_error
from uploader.views import (
    add_series,
    upload_content,
    upload_picture,
    delete_picture
)

urls = {
    'addSeries': add_series,
    'uploadPicture': upload_picture,
    'uploadContent': upload_content,
    'deletePicture': delete_picture,
}


@api_view(http_method_names=['POST'])
def uploader_routing(request, *args, **kwargs):
    return urls[request.api_method](request, *args, **kwargs)
    # if request.api_method not in urls.keys():
    #     return not_found(request, *args, **kwargs)
    # try:
    #     return urls[request.api_method](request, *args, **kwargs)
    # except Exception as e:
    #     log_error(e, request=request)
    #     return Response(status=status.HTTP_409_CONFLICT)


def not_found(request, *args, **kwargs):
    log_error('URL not found', request=request)
    return Response(status=status.HTTP_404_NOT_FOUND)
