from bson import ObjectId
from jose import jwt, JWTError
from rest_framework import status
from pydantic import ValidationError
from rest_framework.response import Response

from config.logger import log_error
from config.settings import SECRET_KEY, JWT_LIFETIME
from config.utils import datetime_now
import config.models


def authentication(request):
    try:
        payload = jwt.decode(request.api_auth, SECRET_KEY, algorithms='HS256')
        admin_obj = config.models.Admin.get_one(_id=ObjectId(payload['admin_id']))
        if not admin_obj:
            log_error('admin dose not exist', request=request)
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        if admin_obj.last_access_time < datetime_now():
            log_error('token is expired', request=request)
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        new_last_access_time = datetime_now() + JWT_LIFETIME
        config.models.Admin.update_one({'_id': admin_obj._id}, last_access_time=new_last_access_time)

    except JWTError as e:
        log_error(f'token is invalid: {e}', request=request)
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    return payload['admin_id']


def permission(request, perm):
    admin = config.models.Admin.get_one(_id=request.user_id)
    for access_group in admin.access_group:
        for access in access_group['accesses']:
            if perm == access:
                return True
    # TODO always return True
    return True


def validate_input(auth=False, perm=None):
    def decorator(func):
        def wrap(request, *args, **kwargs):
            if auth:
                res = authentication(request)
                if isinstance(res, Response):
                    return res
                request.user_id = res
            if perm and not permission(request, perm):
                return Response(data={'detail': 'not permitted'}, status=status.HTTP_400_BAD_REQUEST)
            if len(list(func.__annotations__.values())) != 0:
                serializer = list(func.__annotations__.values())[0]
                try:
                    if hasattr(request, 'user_id'):
                        request.api_data['admin_id'] = request.user_id
                    obj = serializer(**request.api_data)
                except ValidationError as validation_error:
                    log_error({'.'.join(e['loc']): e['msg'] for e in validation_error.errors()}, request=request)
                    return Response(data={'detail': 'invalid body'}, status=status.HTTP_400_BAD_REQUEST)
                kwargs['obj'] = obj
            return func(request, *args, **kwargs)

        return wrap

    return decorator
