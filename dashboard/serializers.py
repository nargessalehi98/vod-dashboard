import math
from datetime import datetime
import re
from typing import Optional, Literal, List

from pydantic import BaseModel, validator, Field

from config.serializers import PaginationSerializer
from config.utils import password_regex_check, email_regex_check, datetime_now, to_jalali
from config.models import Admin, AccessGroup, BsonObjectId, Provider, Content, Genre


class LoginSerializer(BaseModel):
    username: str
    password: str


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


class EditContentSerializer(BaseModel):
    title: Optional[str]
    summery: Optional[str]
    persons_id: Optional[List[str]]
    IMDB_link: Optional[str]
    tags: Optional[List[str]]
    length: Optional[str]  # 03:00:10
    publish_datetime: Optional[datetime]

    series_id: Optional[str]
    season: Optional[int]
    episode: Optional[int]

    language: Optional[Literal['Persian', 'English']]
    genre: Optional[List[str]]
    age: Optional[Literal['Adults', 'Children', 'Both']]
    director_id: Optional[str]
    producer_id: Optional[str]
    actors_id: Optional[List]

    id: str

    @validator('id')
    def validate_id(cls, id, values):
        content = Content.get_one(_id=id)

        if content is None:
            raise ValueError('content dose not exist')

        if content.type == 'Movie' or content.type == 'NewSeries':
            if values.get('series_id') or values.get('season') or values.get('episode'):
                raise ValueError('Movie and SeriesEpisode do not need series data')

        elif content.type == 'SeriesEpisode':
            if values.get('language') or values.get('genre') or values.get('age') or \
                    values.get('director_id') or values.get('producer_id') or values.get('actors_id'):
                raise ValueError('NewSeries dose not need Movie data')

        return id

    @validator('genre')
    def validate_genre(cls, genre):
        for genre_id in genre:
            if Genre.get_one(_id=genre_id) is None:
                raise ValueError('genre is not valid')
        return genre


class EditDashboardProfileSerializer(BaseModel):
    title: Optional[str]
    avatar_id: Optional[str]
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


class GetContentSerializer(PaginationSerializer):
    sort: Optional[Literal['-title', '-publish_datetime', 'title', 'publish_datetime', '-length', 'length',
                           '-total_traffic', 'total_traffic']]
    status: Optional[Literal['Uploading', 'AwaitingConfirmation', 'Published', 'Deleted', 'Rejected', 'IsSeries']]
    provider_id: Optional[str]
    search_text: Optional[str]

    @validator('sort')
    def validate_sort(cls, sort):
        if sort.startswith('-'):
            return sort[1:], -1
        return sort[:], 1


class ContentOutputSerializer(BaseModel):
    id: BsonObjectId = Field(alias='_id')
    title: str
    provider_id: str

    @validator('provider_id')
    def validate_provider(cls, provider_id):
        provider = Provider.get_one(_id=provider_id)
        if provider is None:
            raise ValueError('NO PROVIDER')
        return provider.name


class ContentManagementOutputSerializer(BaseModel):
    id: BsonObjectId = Field(alias='_id')
    title: str
    status: Literal['Uploading', 'AwaitingConfirmation', 'Published', 'Deleted', 'Rejected', 'IsSeries']
    status_description: Optional[str]
    length: str
    publish_datetime: datetime
    total_traffic: float

    @validator('publish_datetime')
    def validate_publish_datetime(cls, publish_datetime):
        return to_jalali(publish_datetime)


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
