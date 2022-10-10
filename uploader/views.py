from rest_framework import status
from rest_framework.response import Response

from config.decoratores import validate_input
from config.models import Content, DataCenterInfo, File, Admin, Person, Provider
from uploader.serializer import AddSeriesSerializer, UploadPictureSerializer, UploadContentSerializer, \
    EditContentSerializer, UploadPictureOutputSerializer, DeletePictureSerializer


@validate_input(auth=True, perm='')
def add_series(request, obj: AddSeriesSerializer):
    content = Content(**obj.dict())
    output = Content.create(**content.dict())
    return Response(data={"inserted_id": str(output.inserted_id)}, status=status.HTTP_200_OK)


@validate_input(auth=True, perm='')
def upload_picture(request, obj: UploadPictureSerializer):
    # TODO add a selector - check with Faezeh
    dc = DataCenterInfo.get_one(_id="632ae49c75e768cae5a64b8a")
    secret = File.make_secret()
    file = File.create(dc_id=dc.id, status='Draft', type=obj.type, download_url='', secret=secret,
                       extension=obj.extension, size=obj.size, name=obj.name)
    output = UploadPictureOutputSerializer(
        secret_key=File.uploader_make_hash(secret, dc.id, obj.source_id, obj.type, str(file.inserted_id)),
        upload_url=dc.upload_url)
    return Response(data=output.dict(), status=status.HTTP_200_OK)


@validate_input(auth=True, perm='')
def upload_content(request, obj: UploadContentSerializer):
    output = Content.create(**obj.dict())
    return Response(data={"inserted_id": str(output.inserted_id)}, status=status.HTTP_200_OK)


@validate_input(auth=True, perm='')
def edit_content(request, obj: EditContentSerializer):
    obj_dict = obj.dict()
    obj_dict.pop('id')
    Content.update_one({'_id': obj.id}, **obj_dict)
    return Response(data={"detail": "content is updated"}, status=status.HTTP_200_OK)


@validate_input(auth=True, perm='')
def delete_picture(request, obj: DeletePictureSerializer):
    res = ''
    if obj.type == 'Avatar':
        res = Admin.update_one({'_id': obj.source_id}, avatar_id="")
        if res.modified_count == 0:
            res = Person.update_one({'_id': obj.source_id}, avatar_id="")
        res = res.modified_count
    if obj.type == 'Logo':
        res = Provider.update_one({'_id': obj.source_id}, logo_file_id="")
        res = res.modified_count
    if obj.type == 'Poster':
        res = Content.update_one({'_id': obj.source_id}, poster_id="")
        res = res.modified_count
    if obj.type == 'Image':
        res = Content.update_variable({'_id': obj.source_id}, {'$pull': {'images_id': obj.picture_id}})
        res = res.modified_count
    if res == 1:
        res = File.delete_one(_id=obj.picture_id)
    if res:
        return Response(data={"detail": f"picture {obj.picture_id} removed"}, status=status.HTTP_200_OK)
    return Response(data={"detail": "something went wrong"}, status=status.HTTP_400_BAD_REQUEST)
