from datetime import timedelta

from django.http.response import HttpResponse
from jose import jwt
from rest_framework import status
from rest_framework.response import Response

from config.decoratores import validate_input
from config.settings import JWT_LIFETIME, SECRET_KEY
from config.utils import datetime_now, json_to_csv_convertor, convert_datetime_to_date_hourly
from dashboard.models import Admin, Access, AccessGroup, File, Provider, DataCenterInfo, Content, ContentAccessLog, \
    TotalTraffic
from dashboard.serializers import (
    LoginSerializer,
    ChangePasswordSerializer,
    AddAdminSerializer,
    EditAdminSerializer,
    GetAdminsSerializer,
    AdminsOutputSerializer,
    EditDashboardProfileSerializer,
    ResetAdminPasswordSerializer,
    AccessOutputSerializer,
    GetAccessGroupSerializer,
    AccessGroupOutputSerializer,
    EditAccessGroupSerializer,
    AddAccessGroupSerializer,
    AddProviderSerializer,
    EditProviderSerializer,
    GetProvidersSerializer,
    ProvidersOutPutSerializer,
    DeleteProviderSerializer,
    GetContentSerializer,
    ContentOutputSerializer,
    EditContentSerializer,
    ProviderExcelSerializer,
    GetChartDataSerializer,
    TopContentSerializer,
    GetTotalTrafficSerializer,
    GetExcelSerializer,
    IspTotalTrafficByContentAccessLogSerializer,
    IspTotalTrafficSerializer
)


@validate_input()
def login(request, obj: LoginSerializer):
    admin = Admin.get_one(username=obj.username)
    if admin is None:
        return Response(data={"data": "Wrong password or username"}, status=status.HTTP_401_UNAUTHORIZED)
    if not admin.check_password(obj.password):
        return Response(data={"data": "Wrong password or username"}, status=status.HTTP_401_UNAUTHORIZED)
    access_payload = {
        'token_type': 'access',
        'admin_id': admin.id,
    }
    new_last_access_time = datetime_now() + JWT_LIFETIME
    admin.update(last_access_time=new_last_access_time)
    token = jwt.encode(access_payload, SECRET_KEY, algorithm='HS256')
    return Response(data={'token': token}, status=status.HTTP_200_OK)


@validate_input(auth=True)
def logout(request):
    Admin.update_one({'_id': request.user_id}, last_access_time=datetime_now())
    return Response(data={"data": "logged out"}, status=status.HTTP_200_OK)


@validate_input(auth=True)
def dashboard_change_password(request, obj: ChangePasswordSerializer):
    Admin.update_one({'_id': request.user_id, 'password': obj.old_password},
                     password=obj.new_password)
    return Response(data={"data": "password has changed"}, status=status.HTTP_200_OK)


@validate_input(auth=True)
def add_admin(request, obj: AddAdminSerializer):
    Admin.create(**obj.dict())
    obj = Admin.get_one(username=obj.username)
    return Response(data={"admin": obj.dict()}, status=status.HTTP_200_OK)


@validate_input(auth=True)
def edit_admin(request, obj: EditAdminSerializer):
    access_group_list = [AccessGroup.get_one(_id=id).dict() for id in obj.access_group_ids]
    obj_dict = obj.dict()
    obj_dict.pop('admin_id')
    obj_dict.pop('access_group_ids')
    obj_dict['access_group'] = access_group_list
    Admin.update_one({'_id': obj.admin_id}, **obj_dict)
    obj = Admin.get_one(_id=obj.admin_id)
    return Response(data={"admin": obj.dict()}, status=status.HTTP_200_OK)


@validate_input(auth=True)
def get_admins(request, obj: GetAdminsSerializer):
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
def get_dashboard_profile(request):
    admin = Admin.get_one(_id=request.user_id)
    return Response(data={"admin": admin.dict()}, status=status.HTTP_200_OK)


@validate_input(auth=True)
def edit_dashboard_profile(request, obj: EditDashboardProfileSerializer):
    admin = Admin.get_one(_id=request.user_id)
    if admin.username == 'admin':
        Admin.update_one({'_id': request.user_id}, **obj.dict())
        admin = Admin.get_one(_id=request.user_id)
        return Response(data={"admin": admin.dict()}, status=status.HTTP_200_OK)
    return Response(data={"data": "access denied"}, status=status.HTTP_200_OK)


@validate_input(auth=True)
def reset_admin_password(request, obj: ResetAdminPasswordSerializer):
    Admin.update_one({'_id': obj.admin_id}, password=obj.new_password)
    admin = Admin.get_one(_id=obj.admin_id)
    return Response(data={"admin": admin.dict()}, status=status.HTTP_200_OK)


@validate_input(auth=True)
def get_access_list(request):
    accesses_list = Access.list()
    accesses = []
    for access in accesses_list:
        access = AccessOutputSerializer(**access)
        accesses.append(access.dict())
    return Response(data={"access": accesses}, status=status.HTTP_200_OK)


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
    AccessGroup.update_one({'_id': obj.access_group_id}, **obj.dict())
    access_group = AccessGroup.get_one(_id=obj.access_group_id)
    return Response(data={"access group": access_group.dict()}, status=status.HTTP_200_OK)


@validate_input(auth=True)
def add_access_group(request, obj: AddAccessGroupSerializer):
    AccessGroup.create(**obj.dict())
    access_group = AccessGroup.get_one(title=obj.title)
    return Response(data={"access group": access_group.dict()}, status=status.HTTP_200_OK)


@validate_input(auth=True, perm='AddProvider')
def add_provider(request, obj: AddProviderSerializer):
    file = File.get_one(_id=obj.logo_file_id)
    data_center = DataCenterInfo.get_one(_id=file.dc_id)
    Provider.create(name=obj.name, dc_id=data_center.id, logo_file_id=obj.logo_file_id,
                    url=f'{data_center.download_url}{file.download_url}')
    provider = Provider.get_one(name=obj.name)
    return Response(data={"provider": provider.dict()}, status=status.HTTP_200_OK)


@validate_input(auth=True, perm='EditProvider')
def edit_provider(request, obj: EditProviderSerializer):
    obj_dict = obj.dict()
    obj_dict.pop('provider_id')
    Provider.update_one({'_id': obj.provider_id}, **obj_dict)
    provider = Provider.get_one(_id=obj.provider_id)
    return Response(data={"provider": provider.dict()}, status=status.HTTP_200_OK)


@validate_input(auth=True, perm='EditProvider')
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


@validate_input(auth=True, perm='ModifyProvider')
def delete_provider(request, obj: DeleteProviderSerializer):
    Provider.delete_one(_id=obj.id)
    return Response(data={"msg": "provider has been deleted"}, status=status.HTTP_200_OK)


@validate_input(auth=True, perm='')
def get_most_visited_contents(request):
    pass


@validate_input(auth=True, perm='')
def get_all_contents(request, obj: GetContentSerializer):
    query = {}
    if obj.sort and obj.filter:
        query = {'status': obj.filter}
    content_list = Content.list(query).skip(obj.skip).limit(obj.limit)
    if obj.sort:
        content_list = content_list.sort(obj.sort)
    contents = []
    for content in content_list:
        content = ContentOutputSerializer(**content)
        contents.append(content.dict())
    return Response(data={"msg": contents}, status=status.HTTP_200_OK)


@validate_input(auth=True, perm='')
def edit_content(request, obj: EditContentSerializer):
    obj_dict = obj.dict()
    obj_dict.pop('id')
    Content.update_one({'_id': obj.id}, **obj_dict)
    return Response(data={"msg": "content is updated"}, status=status.HTTP_200_OK)


@validate_input(auth=True, perm='')
def get_chart_date(request, obj: GetChartDataSerializer):
    output = []
    if 'TopContent' in obj.data_subjects:
        if obj.start_time is None and obj.end_time is None:
            obj.start_time = str(datetime_now().date() - timedelta(days=30)) + "-" + str(datetime_now().time().hour)
            obj.end_time = str(datetime_now().date()) + "-" + str(datetime_now().time().hour)
        contents = ContentAccessLog.aggregate(obj.content_name, obj.provider_id, 'content_id', 'accessed_bytes',
                                              convert_datetime_to_date_hourly(obj.start_time),
                                              convert_datetime_to_date_hourly(obj.end_time),
                                              obj.skip,
                                              obj.limit, None, None)
        top_content = []
        for content in contents:
            content['id'] = content['_id']['content_id']
            content.pop('_id')
            content = TopContentSerializer(**content)
            top_content.append(content.dict())
        output.append(top_content)
    return Response(data={"data": output}, status=status.HTTP_200_OK)


@validate_input(auth=True, perm='')
def get_total_traffic(request, obj: GetTotalTrafficSerializer):
    output = []
    if obj.start_time is None and obj.end_time is None:
        obj.start_time = datetime_now() - timedelta(days=obj.type[1])
        obj.end_time = datetime_now()
    if obj.provider_id is None and obj.content_name is None:
        traffic_list = TotalTraffic.aggregate_set(None, None, 'isp_name', None,
                                                  convert_datetime_to_date_hourly(obj.start_time),
                                                  convert_datetime_to_date_hourly(obj.end_time),
                                                  obj.skip,
                                                  obj.limit, 'date_hourly', 'accessed_bytes')
        for traffic in traffic_list:
            traffic['id'] = traffic['_id']['isp_name']
            traffic.pop('_id')
            traffic = IspTotalTrafficSerializer(**traffic)
            output.append(traffic.dict())
    elif obj.provider_id:
        traffic_list = ContentAccessLog.aggregate_two_group(obj.content_name, obj.provider_id, 'date_hourly',
                                                            'accessed_bytes',
                                                            convert_datetime_to_date_hourly(obj.start_time),
                                                            convert_datetime_to_date_hourly(obj.end_time),
                                                            obj.skip,
                                                            obj.limit)
        for traffic in traffic_list:
            traffic['isp_name'] = traffic['_id']['isp_name']
            traffic['date_hourly'] = traffic['_id']['date_hourly']
            traffic['accessed_bytes'] = traffic['data'][0]['accessed_bytes']
            traffic.pop('_id')
            traffic.pop('data')
            traffic = IspTotalTrafficByContentAccessLogSerializer(**traffic)
            output.append(traffic.dict())
    return Response(data={"data": output}, status=status.HTTP_200_OK)


@validate_input(auth=True, perm='')
def get_excel(request, obj: GetExcelSerializer):
    if obj.type == 'Providers':
        query = {}
        if obj.search_text:
            query = {'name': {'$regex': obj.search_text}}
        providers_list = Provider.list(query)
        providers = []
        for provider in providers_list:
            provider = ProviderExcelSerializer(**provider)
            providers.append(provider.dict())
        json_to_csv_convertor(providers, obj.type, *ProviderExcelSerializer.schema()['properties'].keys())
    if obj.type == 'TopContent':
        if obj.start_time is None and obj.end_time is None:
            obj.start_time = str(datetime_now().date() - timedelta(days=30)) + "-" + str(datetime_now().time().hour)
            obj.end_time = str(datetime_now().date()) + "-" + str(datetime_now().time().hour)
        contents = ContentAccessLog.aggregate(obj.content_name, obj.provider_id, 'content_id', 'accessed_bytes',
                                              convert_datetime_to_date_hourly(obj.start_time),
                                              convert_datetime_to_date_hourly(obj.end_time),
                                              obj.skip,
                                              obj.limit, None, None)
        top_contents = []
        for content in contents:
            content['id'] = content['_id']['content_id']
            content.pop('_id')
            content = TopContentSerializer(**content)
            top_contents.append(content.dict())
        json_to_csv_convertor(top_contents, obj.type, *ProviderExcelSerializer.schema()['properties'].keys())
    if obj.type == 'totalTraffic':
        ...

    with open(f'{obj.type}.csv', 'r') as file:
        response = HttpResponse(file, content_type='csv')
        response['Content-Disposition'] = f'attachment; filename={obj.type}.csv'
        return response
