from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response

from config.decoratores import validate_input
from config.models import File, DataCenterInfo
from internal.serializers import CheckUploadSecretKeySerializer, UpdateUploadStatusSerializer, \
    UpdateUploadStatusOutputSerializer


@validate_input(auth=False, perm='')
def validate_upload_secret_key(request, obj: CheckUploadSecretKeySerializer):
    encoded_secret_key = File.uploader_check_hash(obj.secret_key)
    if File.get_one(_id=encoded_secret_key['file_id'], secret=encoded_secret_key['secret'],
                    dc_id=encoded_secret_key['dc_id']) is not None:
        return Response(data={"detail": "secret key IS valid"}, status=status.HTTP_200_OK)
    return Response(data={"detail": "secret key IS NOT valid"}, status=status.HTTP_200_OK)


@validate_input(auth=False, perm='')
def update_upload_status(request, obj: UpdateUploadStatusSerializer):
    encoded_secret_key = File.uploader_check_hash(obj.secret_key)
    File.update_one({'_id': encoded_secret_key['file_id']}, download_url=obj.download_url)
    res = File.update_source_files_id(encoded_secret_key['type'], encoded_secret_key['source_id'],
                                      encoded_secret_key['file_id'])
    dc = DataCenterInfo.get_one(_id=encoded_secret_key['dc_id'])
    output = UpdateUploadStatusOutputSerializer(download_url=f'{dc.download_url}{obj.download_url}', updated_file=res)
    return Response(data=output.dict(), status=status.HTTP_200_OK)
