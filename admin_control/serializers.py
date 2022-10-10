from datetime import datetime
from typing import Optional, List, Literal, Union

from pydantic import BaseModel, validator, Field

from config.models import Admin, Provider, BsonObjectId, AccessGroup, Tag
from config.serializers import PaginationSerializer
from config.utils import datetime_now, password_regex_check, email_regex_check, to_jalali


class AddAdminSerializer(BaseModel):
    username: str
    password: str
    email: Optional[str]
    title: Optional[str]
    avatar_id: Optional[str]
    access_group_ids: Optional[List]
    last_access_time: datetime = datetime_now()
    status: Literal['Active', 'Deactive'] = 'Active'
    provider_id: Optional[str]

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

    # TODO check access group ids
    # @validator('access_group_ids')
    # def access_group_ids_is_valid(cls, access_group_ids):
    #     for id in access_group_ids:
    #         if AccessGroup.get_one(id=id) is None:
    #             raise ValueError(f'AccessGroup by id {id} is not valid')
    #     return access_group_ids

    @validator('provider_id')
    def provider_id_is_valid(cls, provider_id):
        provider = Provider.get_one(_id=provider_id)
        if provider is None:
            raise ValueError('provider is not valid')
        return provider_id


class AdminOutputSerializer(BaseModel):
    id: str
    username: str
    email: str
    title: str
    avatar_id: str
    status: Literal['Active', 'Deactive']
    access_group_ids: Optional[list]
    last_access_time: datetime
    provider_id: Optional[str]

    @validator('last_access_time', allow_reuse=True)
    def validate_last_access_time(cls, last_access_time):
        return to_jalali(last_access_time)


class EditAdminSerializer(BaseModel):
    admin_id: str
    username: Optional[str]
    title: Optional[str]
    avatar_id: Optional[str]
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
    avatar_id: Optional[str]
    access_group_id: Optional[list]
    last_access_time: Optional[datetime]
    status: Optional[Literal['Active', 'Deactive']]
    provide: Optional[Provider]


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


class AccessGroupSerializer(BaseModel):
    id: str
    title: str
    accesses: list


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


class ProviderOutputSerializer(BaseModel):
    id: str
    name: str
    dc_id: str  # data center id which is in DataCenterServer table
    logo_file_id: str  # file id which is in File table
    url: str  # Relative URL which becomes complete by dc download_url  in ServerInfo table


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
    id: BsonObjectId = Field(alias='_id')
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


class PersonOutputSerializer(BaseModel):
    id: BsonObjectId = Field(alias='_id')
    full_name: str
    role: str
    avatar_id: Optional[str]


class GenreOutputSerializer(BaseModel):
    id: BsonObjectId = Field(alias='_id')
    name: str


class PersonsSerializer(PaginationSerializer):
    role: Literal['Director', 'Producer', 'Actor', 'Other']
    search_text: Optional[str]


class GetTagSerializer(PaginationSerializer):
    search_text: str


class AddTagSerializer(BaseModel):
    name: str

    @validator('name')
    def validate_name(cls, name):
        tag = Tag.get_one(name=name)
        if tag is not None:
            raise ValueError('tag already exist')
        return name


class TagOutputSerializer(BaseModel):
    id: BsonObjectId = Field(alias='_id')
    name: str


class GetGenreSerializer(PaginationSerializer):
    search_text: Optional[str]


class GetSerialsSerializer(PaginationSerializer):
    search_text: Optional[str]


class GetSerialsOutputSerial(BaseModel):
    id: BsonObjectId = Field(alias='_id')
    type: str
    title: str
    summery: str
    language: Literal['Persian', 'English']
    genre: List[str]
    age: Literal['Adults', 'Children', 'Both']
    director_id: str
    producer_id: str
    actors_id: list
    persons_id: Optional[List[str]]
    IMDB_link: Optional[str]
    tags: List[str]
    admin_id: str
    provider_id: Optional[str]
    poster_id: str
