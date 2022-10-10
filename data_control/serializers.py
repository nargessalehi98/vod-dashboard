import math
from datetime import datetime, timedelta
from typing import Literal, Optional, List

from pydantic import validator, BaseModel, Field

from config.models import BsonObjectId, Provider, Content, Genre
from config.serializers import PaginationSerializer
from config.utils import to_jalali, datetime_now


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


class ContentManagementOutputSerializer(BaseModel):
    id: BsonObjectId = Field(alias='_id')
    title: str
    status: Literal['Uploading', 'AwaitingConfirmation', 'Published', 'Deleted', 'Rejected', 'IsSeries']
    status_description: Optional[str]
    length: str
    publish_datetime: datetime
    total_traffic: float = 1

    @validator('publish_datetime')
    def validate_publish_datetime(cls, publish_datetime):
        return to_jalali(publish_datetime)


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


class GetMostVisitedContentSerializer(PaginationSerializer):
    provider_id: Optional[str]
    content_name: Optional[str]
    end_time: Optional[datetime] = datetime_now()
    start_time: Optional[datetime] = datetime_now() - timedelta(days=30)
    get_excel: bool

    @validator('get_excel')
    def validate_skip_and_limit(cls, get_excel, values):
        if get_excel is True:
            if values.get('skip') is not None or values.get('limit') is not None:
                raise ValueError('skip and limit must be noun for excel file')
        return get_excel

    @validator('provider_id')
    def validate_provider_id(cls, provider_id):
        if Provider.get_one(_id=provider_id) is None:
            raise ValueError('Provider id is not valid')

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


class GetTotalTrafficSerializer(BaseModel):
    provider_id: Optional[str]
    content_name: Optional[str]
    content_id: Optional[str]
    end_time: Optional[datetime] = datetime_now()
    start_time: Optional[datetime] = datetime_now() - timedelta(days=100)
    type: Optional[Literal['Daily', 'Hourly']]
    get_excel: bool

    @validator('provider_id')
    def validate_provider_id(cls, provider_id):
        if Provider.get_one(_id=provider_id) is None:
            raise ValueError('Provider id is not valid')
        return provider_id

    @validator('content_name')
    def validate_content_name(cls, content_name):
        contents = Content.list({'title': {'$regex': content_name}})
        content_ids = []
        for content in contents:
            content_ids.append(str(content['_id']))
        return content_ids

    # @validator('content_id')
    # def validate_content_id(cls, content_id):
    #     content = Content.get_one({'_id': content_id})
    #     if content is None:
    #         raise ValueError('content id is not valid')
    #     return content

    @validator('start_time')
    def start_time_is_valid(cls, start_time, values):
        interval = values.get('end_time') - start_time
        if math.fabs(interval.days) >= 300:
            raise ValueError('interval is too big')
        return start_time

    @validator('type')
    def type_validator(cls, type, values):
        days = (values.get('end_time') - values.get('start_time')).days
        if type == 'Daily':
            if days <= 100:
                return type, 1
            return type, math.ceil(days / 100)
        if type == 'Hourly':
            if (days * 24) <= 96:
                return type, 1
            return type, math.ceil((days * 24) / 100)


class ISPTotalTrafficSerializer(BaseModel):
    isp_name: Literal['MTN', 'MCI', 'Other']
    date_hourly: list
    accessed_bytes: list


class ContentSegmentAccessCountSerializer(BaseModel):
    content_id: str
    get_excel: bool

    @validator('content_id')
    def validate_provider_id(cls, content_id):
        if Content.get_one(_id=content_id) is None:
            raise ValueError('content_id  is not valid')
        return content_id


class ContentSegmentAccessCountOutputSerializer(BaseModel):
    segment: str
    access_count: int
