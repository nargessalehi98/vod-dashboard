from jose import jwt
from rest_framework import status
from rest_framework.response import Response

from config.decoratores import validate_input
from config.logger import log_error
from config.settings import JWT_LIFETIME, SECRET_KEY
from config.utils import datetime_now
from config.models import Admin
from dashboard.serializers import (
    LoginSerializer,
    ChangePasswordSerializer,
    EditDashboardProfileSerializer,
    ResetAdminPasswordSerializer,
    AdminOutputSerializer,
)


@validate_input()
def login(request, obj: LoginSerializer):
    admin = Admin.get_one(username=obj.username)
    if admin is None:
        log_error('invalid username', request=request)
        return Response(data={"detail": "Wrong password or username"}, status=status.HTTP_401_UNAUTHORIZED)
    if not admin.check_password(obj.password):
        log_error('invalid password', request=request)
        return Response(data={"detail": "Wrong password or username"}, status=status.HTTP_401_UNAUTHORIZED)
    access_payload = {
        'token_type': 'access',
        'admin_id': admin.id,
    }
    new_last_access_time = datetime_now() + JWT_LIFETIME
    admin.update(last_access_time=new_last_access_time)
    token = jwt.encode(access_payload, SECRET_KEY, algorithm='HS256')
    admin = AdminOutputSerializer(**admin.dict())
    return Response(data={'token': token, 'admin': admin.dict()}, status=status.HTTP_200_OK)


@validate_input(auth=True)
def logout(request):
    Admin.update_one({'_id': request.user_id}, last_access_time=datetime_now())
    return Response(data={"detail": "logged out"}, status=status.HTTP_200_OK)


@validate_input(auth=True)
def dashboard_change_password(request, obj: ChangePasswordSerializer):
    Admin.update_one({'_id': request.user_id, 'password': obj.old_password},
                     password=obj.new_password)
    return Response(data={"detail": "password has changed"}, status=status.HTTP_200_OK)


@validate_input(auth=True)
def get_dashboard_profile(request):
    admin = Admin.get_one(_id=request.user_id)
    admin = AdminOutputSerializer(**admin.dict())
    return Response(data={"admin": admin.dict()}, status=status.HTTP_200_OK)


@validate_input(auth=True)
def edit_dashboard_profile(request, obj: EditDashboardProfileSerializer):
    admin = Admin.get_one(_id=request.user_id)
    if admin.username == 'admin':
        Admin.update_one({'_id': request.user_id}, **obj.dict())
        admin = Admin.get_one(_id=request.user_id)
        admin = AdminOutputSerializer(**admin.dict())
        return Response(data={"admin": admin.dict()}, status=status.HTTP_200_OK)
    log_error('access denied', request=request)
    return Response(data={"detail": "access denied"}, status=status.HTTP_200_OK)


@validate_input(auth=True)
def reset_admin_password(request, obj: ResetAdminPasswordSerializer):
    Admin.update_one({'_id': obj.admin_id}, password=obj.new_password)
    admin = Admin.get_one(_id=obj.admin_id)
    admin = AdminOutputSerializer(**admin.dict())
    return Response(data={"admin": admin.dict()}, status=status.HTTP_200_OK)
