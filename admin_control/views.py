from rest_framework import status
from rest_framework.response import Response

from admin_control.serializers import (
    AddAdminSerializer,
    AdminOutputSerializer,
    EditAdminSerializer,
    GetAdminsSerializer,
    AdminsOutputSerializer,
    AddAccessGroupSerializer,
    AccessGroupSerializer,
    GetAccessGroupSerializer,
    AccessGroupOutputSerializer,
    EditAccessGroupSerializer,
    AddProviderSerializer,
    ProviderOutputSerializer,
    EditProviderSerializer,
    GetProvidersSerializer,
    ProvidersOutPutSerializer,
    DeleteProviderSerializer,
    PersonOutputSerializer,
    GenreOutputSerializer,
    PersonsSerializer,
    TagOutputSerializer,
    GetGenreSerializer,
    AddTagSerializer,
    GetTagSerializer, GetSerialsSerializer, GetSerialsOutputSerial)
from config.decoratores import validate_input
from config.models import Admin, AccessGroup, Access, Provider, DataCenterInfo, File, Person, Genre, Tag, Content
from dashboard.serializers import AccessOutputSerializer


@validate_input(auth=True)
def add_admin(request, obj: AddAdminSerializer):
    Admin.create(**obj.dict())
    obj = Admin.get_one(username=obj.username)
    admin = AdminOutputSerializer(**obj.dict())
    return Response(data={"admin": admin.dict()}, status=status.HTTP_200_OK)


@validate_input(auth=True)
def edit_admin(request, obj: EditAdminSerializer):
    if obj.access_group_ids is not None:
        access_group_list = [AccessGroup.get_one(_id=id).dict() for id in obj.access_group_ids]
    else:
        access_group_list = []
    obj_dict = obj.dict()
    obj_dict.pop('admin_id')
    obj_dict.pop('access_group_ids')
    obj_dict['access_group'] = access_group_list
    Admin.update_one({'_id': obj.admin_id}, **obj_dict)
    obj = Admin.get_one(_id=obj.admin_id)
    admin = AdminOutputSerializer(**obj.dict())
    return Response(data={"admin": admin.dict()}, status=status.HTTP_200_OK)


@validate_input(auth=True)
def get_admins(request, obj: GetAdminsSerializer):
    query = {}
    if obj.access_group_ids and obj.search_text:
        query = {'$or': [{'username': {'$regex': obj.search_text}}, {'email': {'$regex': obj.search_text}},
                         {'title': {'$regex': obj.search_text}}], 'status': obj.status,
                 'access_group_ids': {'$all': obj.access_group_ids}}
    elif obj.search_text is None and obj.access_group_ids is not None:
        query = {'status': obj.status, 'access_group_ids': {'$all': obj.access_group_ids}}
    else:
        query = {'status': obj.status}
    admins = []
    all_admins = Admin.list(query).skip(obj.skip).limit(obj.limit)
    count = Admin.count(query)
    for admin in all_admins:
        admin = AdminsOutputSerializer(**admin)
        admins.append(admin.dict())
    return Response(data={"admins": admins, "count": count}, status=status.HTTP_200_OK)


@validate_input(auth=True)
def get_access_list(request):
    accesses_list = Access.list()
    accesses = []
    for access in accesses_list:
        access = AccessOutputSerializer(**access)
        accesses.append(access.dict())
    return Response(data={"access": accesses}, status=status.HTTP_200_OK)


@validate_input(auth=True)
def add_access_group(request, obj: AddAccessGroupSerializer):
    AccessGroup.create(**obj.dict())
    access_group = AccessGroup.get_one(title=obj.title)
    access_group = AccessGroupSerializer(**access_group.dict())
    return Response(data={"access group": access_group.dict()}, status=status.HTTP_200_OK)


@validate_input(auth=True)
def get_access_groups(request, obj: GetAccessGroupSerializer):
    query = {}
    if obj.search_text:
        query = {'accesses': {'$all': obj.search_text}}
    access_groups_list = AccessGroup.list(query).skip(obj.skip).limit(obj.limit)
    access_groups = []
    for access_group in access_groups_list:
        access_group = AccessGroupOutputSerializer(**access_group)
        access_groups.append(access_group.dict())
    return Response(data={"access groups": access_groups}, status=status.HTTP_200_OK)


@validate_input(auth=True)
def edit_access_groups(request, obj: EditAccessGroupSerializer):
    access_group_id = obj.access_group_id
    obj_dict = obj.dict()
    obj_dict.pop('access_group_id')
    AccessGroup.update_one({'_id': access_group_id}, **obj_dict)
    access_group = AccessGroup.get_one(_id=access_group_id)
    access_group = AccessGroupSerializer(**access_group.dict())
    return Response(data={"access group": access_group.dict()}, status=status.HTTP_200_OK)


@validate_input(auth=True, perm='')
def add_provider(request, obj: AddProviderSerializer):
    file = File.get_one(_id=obj.logo_file_id)
    data_center = DataCenterInfo.get_one(_id=file.dc_id)
    Provider.create(name=obj.name, dc_id=data_center.id, logo_file_id=obj.logo_file_id,
                    url=f'{data_center.download_url}{file.download_url}')
    provider = Provider.get_one(name=obj.name)
    provider = ProviderOutputSerializer(**provider.dict())
    return Response(data={"provider": provider.dict()}, status=status.HTTP_200_OK)


@validate_input(auth=True, perm='')
def edit_provider(request, obj: EditProviderSerializer):
    obj_dict = obj.dict()
    obj_dict.pop('provider_id')
    if obj.logo_file_id:
        file = File.get_one(_id=obj.logo_file_id)
        data_center = DataCenterInfo.get_one(_id=file.dc_id)
        obj_dict['dc_id'] = data_center.id
        obj_dict['url'] = f'{data_center.download_url}{file.download_url}'
    Provider.update_one({'_id': obj.provider_id}, **obj_dict)
    provider = Provider.get_one(_id=obj.provider_id)
    provider = ProviderOutputSerializer(**provider.dict())
    return Response(data={"provider": provider.dict()}, status=status.HTTP_200_OK)


@validate_input(auth=True, perm='')
def get_providers(request, obj: GetProvidersSerializer):
    query = {}
    if obj.search_text:
        query = {'name': {'$regex': obj.search_text}}
    providers_list = Provider.list(query).skip(obj.skip).limit(obj.limit)
    providers = []
    for provider in providers_list:
        provider = ProvidersOutPutSerializer(**provider)
        providers.append(provider.dict())
    return Response(data={"providers": providers}, status=status.HTTP_200_OK)


@validate_input(auth=True, perm='')
def delete_provider(request, obj: DeleteProviderSerializer):
    Provider.delete_one(_id=obj.id)
    return Response(data={"detail": "provider has been deleted"}, status=status.HTTP_200_OK)


@validate_input(auth=True, perm='')
def get_persons(request, obj: PersonsSerializer):
    query = {'role': obj.role}
    if obj.search_text:
        query = {'role': obj.role, 'full_name': {'$regex': obj.search_text}}
    persons = Person.list(query).skip(obj.skip).limit(obj.limit)
    output = []
    for person in persons:
        person = PersonOutputSerializer(**person)
        output.append(person.dict())
    return Response(data=output, status=status.HTTP_200_OK)


@validate_input(auth=True, perm='')
def get_genres(request, obj: GetGenreSerializer):
    query = {}
    if obj.search_text:
        query = {'name': {'$regex': obj.search_text}}
    genres = Genre.list(query).skip(obj.skip).limit(obj.limit)
    output = []
    for genre in genres:
        genre = GenreOutputSerializer(**genre)
        output.append(genre.dict())
    return Response(data=output, status=status.HTTP_200_OK)


@validate_input(auth=True, perm='')
def add_tag(request, obj: AddTagSerializer):
    tag = Tag.create(name=obj.name)
    return Response(data={'name': obj.name, 'id': str(tag.inserted_id)}, status=status.HTTP_200_OK)


@validate_input(auth=True, perm='')
def get_tag(request, obj: GetTagSerializer):
    tags = Tag.list({'name': {'$regex': obj.search_text}})
    output = []
    for tag in tags:
        tag = TagOutputSerializer(**tag)
        output.append(tag.dict())
    return Response(data=output, status=status.HTTP_200_OK)


@validate_input(auth=True, perm='')
def get_serials(request, obj: GetSerialsSerializer):
    query = {}
    if obj.search_text:
        query = {'title': {'$regex': obj.search_text}}
    serials = Content.list(query, type='NewSeries')
    output = []
    for serial in serials:
        serial = GetSerialsOutputSerial(**serial)
        output.append(serial.dict())
    return Response(data=output, status=status.HTTP_200_OK)
