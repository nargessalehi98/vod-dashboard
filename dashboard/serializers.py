import math
from datetime import datetime, timedelta
import re
from typing import Optional, Literal, List

from pydantic import BaseModel, validator, Field

from config.serializers import PaginationSerializer
from config.utils import password_regex_check, email_regex_check, datetime_now
from dashboard.models import Admin, AccessGroup, BsonObjectId, Provider, Content


class LoginSerializer(BaseModel):
    username: str
    password: str


class ChangePasswordSerializer(BaseModel):
    old_password: str
    new_password: str

    @validator('new_password')
    def new_password_is_valid(cls, new_password):
        if not password_regex_check:
            raise ValueError('password is not valid')
        return Admin.make_password(new_password)

    @validator('old_password')
    def old_password_is_valid(cls, old_password):
        return Admin.make_password(old_password)


class AddAdminSerializer(BaseModel):
    username: str
    password: str
    title: str
    provider_id: str
    avatar_url: Optional[str]
    email: Optional[str]
    access_group_ids: Optional[list]

    @validator('username')
    def username_is_valid(cls, username):
        admin = Admin.get_one(username=username)
        if admin:
            raise ValueError('username already exist')
        return username

    @validator('password')
    def password_is_valid(cls, password):
        if not password_regex_check:
            raise ValueError('password is not valid')
        return Admin.make_password(password)

    @validator('email')
    def email_is_valid(cls, email):
        if not email_regex_check:
            raise ValueError('email is not valid')
        if Admin.get_one(email=email):
            raise ValueError('email has registered')
        return email

    @validator('access_group_ids')
    def access_group_ids_is_valid(cls, access_group_ids):
        for id in access_group_ids:
            if AccessGroup.get_one(id=id) is None:
                raise ValueError(f'AccessGroup by id {id} is not valid')
        return access_group_ids

    @validator('provider_id')
    def provider_id_is_valid(cls, provider_id):
        if Provider.get_one(_id=provider_id) is None:
            raise ValueError('provider is not valid')
        return provider_id


class EditAdminSerializer(BaseModel):
    admin_id: str
    username: Optional[str]
    title: Optional[str]
    avatar_url: Optional[str]
    email: Optional[str]
    status: Optional[Literal['Active', 'Deactive']]
    access_group_ids: Optional[list]

    @validator('username')
    def username_is_valid(cls, username):
        admin = Admin.get_one(username=username)
        if admin:
            raise ValueError('username already exist')
        return username

    @validator('email')
    def email_is_valid(cls, email):
        if not email_regex_check:
            raise ValueError('email is not valid')
        if Admin.get_one(email=email):
            raise ValueError('email has registered')
        return email

    # TODO check it later
    # @validator('access_group_ids')
    # def access_group_ids_is_valid(cls, access_group_ids):
    #     for id in access_group_ids:
    #         if AccessGroup.get_one(id=id) is None:
    #             raise ValueError(f'AccessGroup by id {id} is not valid')
    #     return access_group_ids


class GetAdminsSerializer(PaginationSerializer):
    status: Optional[Literal['Active', 'Deactive']]
    access_group_ids: Optional[list]
    search_text: Optional[str]

    # TODO leave it for now,it should be complete.
    # @validator('access_group_ids')
    # def access_group_ids_is_valid(cls, access_group_ids):
    #     for id in access_group_ids:
    #         if AccessGroup.get_one(id=id) is None:
    #             raise ValueError(f'AccessGroup by id {id} is not valid')
    #     return access_group_ids


class AdminsOutputSerializer(BaseModel):
    id: BsonObjectId = Field(alias='_id')
    username: str
    email: Optional[str]
    title: Optional[str]
    avatar_url: Optional[str]
    access_group_id: Optional[list]
    last_access_time: Optional[datetime]
    status: Optional[Literal['Active', 'Deactive']]
    provide: Optional[Provider]


class EditDashboardProfileSerializer(BaseModel):
    title: Optional[str]
    avatar_url: Optional[str]
    email: Optional[str]

    @validator('email')
    def email_is_valid(cls, email):
        if not email_regex_check(email):
            raise ValueError('email is not valid')
        if Admin.get_one(email=email):
            raise ValueError('email has registered')
        return email


class ResetAdminPasswordSerializer(BaseModel):
    admin_id: str
    new_password: str

    @validator('new_password')
    def password_is_valid(cls, new_password):
        rx = re.compile(r'^(?=.*\d).{8,}$')
        if not rx.match(new_password):
            raise ValueError('password is not valid')
        return Admin.make_password(new_password)

    @validator('admin_id')
    def username_is_valid(cls, admin_id):
        admin = Admin.get_one(_id=admin_id)
        if not admin:
            raise ValueError('Admin dose not exist')
        return admin_id


class AccessOutputSerializer(BaseModel):
    id: BsonObjectId = Field(alias='_id')
    access: str


class GetAccessGroupSerializer(PaginationSerializer):
    limit: int
    skip: int
    search_text: Optional[list]


class AccessGroupOutputSerializer(BaseModel):
    id: BsonObjectId = Field(alias='_id')
    title: str
    accesses: list


class EditAccessGroupSerializer(BaseModel):
    access_group_id: str
    title: Optional[str]
    accesses: Optional[list]

    # TODO leave it for now,it should be complete.
    # @validator('access')
    # def access_group_ids_is_valid(cls, access):
    #     for id in access:
    #         if AccessGroup.get_one(id=id) is None:
    #             raise ValueError(f'AccessGroup by id {id} is not valid')
    #     return access_group_ids


class AddAccessGroupSerializer(BaseModel):
    title: Optional[str]
    accesses: Optional[list]

    @validator('title')
    def access_group_ids_is_valid(cls, title):
        access_group = AccessGroup.get_one(title=title)
        if access_group:
            raise ValueError('title is not valid')
        return title

    # TODO leave it for now,it should be complete.
    # @validator('access')
    # def access_group_ids_is_valid(cls, access):
    #     for id in access:
    #         if AccessGroup.get_one(id=id) is None:
    #             raise ValueError(f'AccessGroup by id {id} is not valid')
    #     return access_group_ids


class AddProviderSerializer(BaseModel):
    name: str
    logo_file_id: str

    # @validator('name')
    # def provider_id_is_valid(cls, name):
    #     if not Provider.get_one(name=name):
    #         raise ValueError('name id is not valid')
    #     return name

    # @validator('logo_file_id')
    # def logo_file_id_is_valid(cls, logo_file_id):
    #     if not Provider.get_one(_id=logo_file_id):
    #         raise ValueError('logo_file_id id is not valid')
    #     return logo_file_id


class EditProviderSerializer(BaseModel):
    provider_id: str
    name: Optional[str]
    logo_file_id: Optional[str]

    @validator('provider_id')
    def provider_id_is_valid(cls, provider_id):
        if not Provider.get_one(_id=provider_id):
            raise ValueError('Provider id is not valid')
        return provider_id

    @validator('logo_file_id')
    def logo_file_id_is_valid(cls, logo_file_id):
        if not Provider.get_one(logo_file_id=logo_file_id):
            raise ValueError('logo_file_id id is not valid')
        return logo_file_id


class GetProvidersSerializer(PaginationSerializer):
    search_text: Optional[str]


class ProvidersOutPutSerializer(BaseModel):
    name: str
    dc_id: str
    logo_file_id: str
    url: str


class DeleteProviderSerializer(BaseModel):
    id: str

    @validator('id')
    def logo_file_id_is_valid(cls, id):
        if not Provider.get_one(_id=id):
            raise ValueError(' id is not valid')
        return id


class GetContentSerializer(PaginationSerializer):
    sort: Optional[Literal['-title', '-publish_datetime', 'title', 'publish_datetime']]
    status: Optional[Literal[
        'Uploading', 'AwaitingConfirmation', 'QueuingPublication', 'Published', 'Deleted', 'Rejected', 'ReadyPublish']]

    @validator('sort')
    def validate_sort(cls, sort):
        if sort.startswith('-'):
            return sort[1:], -1
        return sort[1:], 1


class ContentOutputSerializer(BaseModel):
    title: str
    status: Literal[
        'Uploading', 'AwaitingConfirmation', 'QueuingPublication', 'Published', 'Deleted', 'Rejected', 'ReadyPublish']
    status_description: Optional[str]
    length: timedelta
    publish_datetime: Optional[datetime]


class EditContentSerializer(BaseModel):
    id: str
    title: Optional[str]
    director: Optional[str]
    producer: Optional[str]
    summery: Optional[str]
    actors: Optional[list]
    language: Optional[str]
    genre: Optional[List[Literal[
        'Action', 'Comedy', 'Horror', 'Sci-Fi', 'Western', 'Romance', 'Thriller', 'Fantasy', 'Historical', 'Crime',
        'Mystery', 'Drama', 'Animation', 'Experimental', 'Musical', 'War', 'Biographical']]]
    IMDB_link: Optional[str]
    age: Optional[Literal['G', 'PG', 'PG-13', 'R', 'NC-17']]
    status: Optional[Literal[
        'Uploading', 'AwaitingConfirmation', 'QueuingPublication', 'Published', 'Deleted', 'Rejected', 'ReadyPublish']]
    status_description: Optional[str]
    tags: Optional[list]
    poster_id: Optional[str]
    images_ids: Optional[list]
    comments: Literal['']
    length: Optional[timedelta]
    publish_datetime: Optional[datetime]

    @validator('id')
    def id_is_valid(cls, id):
        if Content.get_one(_id=id) is None:
            raise ValueError('id is not valid')

    @validator('genre')
    def validate_genre(cls, genre):
        return list(set(Content.get_one(_id=id).genre + genre))

    @validator('status_description')
    def validate_status_description(cls, status_description, values):
        if values.get('status') == 'Rejected' and status_description is None:
            raise ValueError('status_description must have a value')
        return status_description


class GetExcelSerializer(PaginationSerializer):
    type: str
    search_text: Optional[str]
    provider_id: Optional[str]
    content_name: Optional[str]
    end_time: Optional[datetime]
    start_time: Optional[datetime]

    @validator('content_name')
    def validate_content_name(cls, content_name):
        contents = Content.list({'title': {'$regex': content_name}})
        content_ids = []
        for content in contents:
            content_ids.append(str(content['_id']))
        return content_ids

    @validator('start_time')
    def start_time_is_valid(cls, start_time, values):
        interval = values.get('end_time') - start_time
        if math.fabs(interval.days) >= 365:
            raise ValueError('interval is too big')
        return start_time


class ProviderExcelSerializer(BaseModel):
    name: str


class GetChartDataSerializer(PaginationSerializer):
    data_subjects: List[Literal['MTNTraffic', 'MCITraffic', 'OtherTraffic', 'TotalTraffic',
                                'ContentSegment',
                                'ContentISP',
                                'TopContent']]
    provider_id: Optional[str]
    content_name: Optional[str]
    end_time: Optional[datetime]
    start_time: Optional[datetime]
    type: Optional[Literal['Daily', 'Hourly']]

    # TODO uncomment this
    # @validator('provider_id')
    # def validate_provider_id(cls, provider_id):
    #     if Provider.get_one(_id=provider_id) is None:
    #         raise ValueError('Provider id is not valid')

    @validator('content_name')
    def validate_content_name(cls, content_name):
        contents = Content.list({'title': {'$regex': content_name}})
        content_ids = []
        for content in contents:
            content_ids.append(str(content['_id']))
        return content_ids

    @validator('start_time')
    def start_time_is_valid(cls, start_time, values):
        interval = values.get('end_time') - start_time
        if math.fabs(interval.days) >= 365:
            raise ValueError('interval is too big')
        return start_time


class GetTotalTrafficSerializer(PaginationSerializer):
    data_subjects: List[Literal['MTNTraffic', 'MCITraffic', 'OtherTraffic', 'TotalTraffic']]
    provider_id: Optional[str]
    content_name: Optional[str]
    end_time: Optional[datetime]
    start_time: Optional[datetime]
    type: Optional[Literal['Daily', 'Hourly']]

    # TODO uncomment this
    # @validator('provider_id')
    # def validate_provider_id(cls, provider_id):
    #     if Provider.get_one(_id=provider_id) is None:
    #         raise ValueError('Provider id is not valid')

    @validator('content_name')
    def validate_content_name(cls, content_name):
        contents = Content.list({'title': {'$regex': content_name}})
        content_ids = []
        for content in contents:
            content_ids.append(str(content['_id']))
        return content_ids

    @validator('start_time')
    def start_time_is_valid(cls, start_time, values):
        interval = values.get('end_time') - start_time
        if math.fabs(interval.days) >= 365:
            raise ValueError('interval is too big')
        return start_time

    @validator('type')
    def type_validator(cls, type, values):
        if values.get('end_time') is not None and values.get('start_time') is not None:
            days = (values.get('end_time') - values.get('start_time')).days
            if type == 'Daily':
                if days <= 100:
                    return type, 1
                return type, math.ceil(days / 100)
            if type == 'Hourly':
                if (days * 24) <= 96:
                    return type, 1
                return type, math.ceil((days * 24) / 100)
        elif type == 'Daily':
            return type, 100
        return type, 4


class IspTotalTrafficSerializer(BaseModel):
    id: Literal['MTN', 'MCI', 'Other']
    date_time: list
    accessed_bytes: list


class IspTotalTrafficByContentAccessLogSerializer(BaseModel):
    date_hourly: str
    isp_name: str
    accessed_bytes: float


class TopContentSerializer(BaseModel):
    id: str
    accessed_bytes: float

    @validator('id')
    def validate_id(cls, _id):
        content = Content.get_one(_id=_id)
        return content.title

    @validator('accessed_bytes')
    def validate_accessed_bytes(cls, accessed_bytes):
        return accessed_bytes / 1000000000
