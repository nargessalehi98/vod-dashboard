import hashlib
import random
import string
from typing import Optional, Literal, List

import jose
from bson import ObjectId
from bson.errors import BSONError
from jose import jwt
from pydantic import BaseModel, Field

from config.queries import Query
from datetime import datetime

from config.settings import SECRET_KEY
from config.utils import datetime_now, convert_datetime_to_date_hourly
from config.settings import db  # # # Do Not Delete This Import


class BsonObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if isinstance(v, str):
            try:
                ObjectId(v)
            except BSONError:
                raise TypeError('Invalid ObjectId')
        elif not isinstance(v, ObjectId):
            raise TypeError('ObjectId required')
        return str(v)


class Access(BaseModel, Query):
    id: BsonObjectId = Field(alias='_id')
    access: Literal[
        'AddAdmin', 'ModifyAdmin', ' ViewAdmin', 'EditDashboardProfile', 'ViewAccessGroup', 'AddAccessGroup',
        'AddProvider', 'ModifyProvider', 'ViewProvider']


class AccessGroup(BaseModel, Query):
    id: BsonObjectId = Field(alias='_id')
    title: str
    accesses: list


class Provider(BaseModel, Query):
    id: BsonObjectId = Field(alias='_id')
    name: str
    dc_id: str  # data center id which is in DataCenterServer table
    logo_file_id: str  # file id which is in File table
    url: str  # Relative URL which becomes complete by dc download_url  in ServerInfo table


class Admin(BaseModel, Query):
    id: BsonObjectId = Field(alias='_id')
    username: str
    password: str
    super_admin: bool = False
    email: Optional[str]
    title: Optional[str]
    avatar_id: Optional[str]
    access_group_ids: Optional[List]
    last_access_time: datetime = datetime_now()
    status: Literal['Active', 'Deactive'] = 'Active'
    provider_id: Optional[str]

    @property
    def is_super_admin(self):
        return self.super_admin

    @property
    def _id(self):
        return ObjectId(self.id) if self.id else None

    def check_password(self, raw_password: str):
        return self.password == hashlib.md5(raw_password.encode('utf-8')).hexdigest()

    @classmethod
    def make_password(cls, raw_password):
        return hashlib.md5(raw_password.encode('utf-8')).hexdigest()


class DataCenterInfo(BaseModel, Query):
    id: BsonObjectId = Field(alias='_id')
    download_url: str
    upload_url: str


class File(BaseModel, Query):
    id: BsonObjectId = Field(alias='_id')
    dc_id: str
    status: Literal['Draft', 'Done']
    type: Literal['Avatar', 'Logo', 'Poster', 'Image']
    secret: str
    download_url: str
    extension: str
    size: int
    name: str

    @classmethod
    def make_secret(cls):
        return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(15))

    @classmethod
    def uploader_check_hash(cls, key):
        try:
            return jwt.decode(key, SECRET_KEY)
        except jose.exceptions.JWTError as e:
            raise ValueError('secret key is not valid')

    @classmethod
    def update_source_files_id(cls, type, source_id, file_id):
        if type == 'Avatar':
            res = Admin.update_one({'_id': source_id}, avatar_id=file_id)
            if res.modified_count == 0:
                res = Person.update_one({'_id': source_id}, avatar_id=file_id)
            return res.modified_count
        if type == 'Logo':
            res = Provider.update_one({'_id': source_id}, logo_file_id=file_id)
            return res.modified_count
        if type == 'Poster':
            res = Content.update_one({'_id': source_id}, poster_id=file_id)
            return res.modified_count
        if type == 'Image':
            content = Content.get_one(_id=source_id)
            if len(content.images_id) >= 10:
                Content.update_variable({'_id': source_id}, {'$pop': {'images_id': -1}})
            res = Content.update_variable({'_id': source_id}, {'$push': {'images_id': file_id}})
            return res.modified_count

    @classmethod
    def uploader_make_hash(cls, secret, dc_id, source_id, type, file_id):
        data = {
            'secret': secret,
            'dc_id': dc_id,
            'source_id': source_id,
            'type': type,
            'file_id': file_id
        }
        return jwt.encode(data, SECRET_KEY, algorithm='HS256')


class Genre(BaseModel, Query):
    id: BsonObjectId = Field(alias='_id')
    name: str


class Tag(BaseModel, Query):
    id: BsonObjectId = Field(alias='_id')
    name: str


# TODO clear category Enum or Model
class Category(BaseModel, Query):
    id: BsonObjectId = Field(alias='_id')
    name: str


class Content(BaseModel, Query):
    id: BsonObjectId = Field(alias='_id', default=None)
    title: str
    type: Literal['Movie', 'SeriesEpisode', 'NewSeries'] = ''
    series_id: Optional[str]
    season: Optional[int]
    episode: Optional[int]
    summery: str
    language: Literal['Persian', 'English']
    genre: List[str]
    # TODO clear category Enum or Model
    # category: str
    age: Literal['Adults', 'Children', 'Both']
    director_id: str
    producer_id: str
    persons_id: Optional[List[str]]
    actors_id: list
    IMDB_link: Optional[str]
    tags: Optional[List[str]]

    status: Literal['Uploading', 'AwaitingConfirmation', 'Published', 'Deleted', 'Rejected', 'IsSeries'] = 'IsSeries'
    status_description: Optional[str]

    poster_id: Optional[str] = []
    images_id: Optional[list] = []

    length: Optional[str] = "00:00:00"  # 03:00:10
    publish_datetime: Optional[datetime] = datetime_now()

    admin_id: str
    provider_id: str

    MCI_traffic: Optional[float] = 0.0
    MTN_traffic: Optional[float] = 0.0
    Other_traffic: Optional[float] = 0.0
    total_traffic: Optional[float] = 0.0


class Person(BaseModel, Query):
    id: BsonObjectId = Field(alias='_id')
    full_name: str
    role: Literal['Director', 'Producer', 'Actor', 'Other']
    avatar_id: str


class ContentAccessLog(BaseModel, Query):
    id: BsonObjectId = Field(alias='_id')
    content_id: str
    provider_id: str
    date_hourly: str  # "2022-10-12-23"
    isp_name: Literal['MCI', 'MTN', 'Other']
    accessed_bytes: int
    traffic_factor: float = 1  # 1/traffic_factor per day

    @classmethod
    def traffic_pipline(cls, start_time, end_time, provider_id, content_id):
        match_list = [{'$and': [
            {'date_hourly': {
                '$gt': convert_datetime_to_date_hourly(start_time),
                '$lt': convert_datetime_to_date_hourly(end_time)
            }},
        ]}]
        if provider_id:
            match_list.append({'provider_id': {'$eq': provider_id}})
        if content_id:
            match_list.append({'content_id': {'$eq': content_id}})
        sort = {'$sort': {'date_hourly': -1}}
        group_list = [{'$group': {
            '_id': {'isp_name': '$isp_name'},
            'isp_name': {'$first': '$isp_name'},
            'date_hourly': {'$push': '$date_hourly'},
            'accessed_bytes': {
                '$push': {'$multiply': ['$traffic_factor', '$accessed_bytes']}
            }}}]
        project = {'_id': 0, 'data': 0}
        return match_list, group_list, project, 'date_hourly', 'isp_name'

    @classmethod
    def get_total_traffic(cls, start_time, end_time, provider_id, content_id):
        return cls.aggregate(*cls.traffic_pipline(start_time, end_time, provider_id, content_id), skip=None, limit=None)


class TotalTraffic(BaseModel, Query):
    id: BsonObjectId = Field(alias='_id')
    date_hourly: str  # "2022-10-12-23"
    isp_name: Literal['MCI', 'MTN', 'Other']
    accessed_bytes: int
    traffic_factor: float = 1

    @classmethod
    def get_total_traffic(cls, start_time, end_time):
        return cls.aggregate(*ContentAccessLog.traffic_pipline(start_time, end_time, None, None), None, None)


class ContentAccessCountLog(BaseModel, Query):
    id: BsonObjectId = Field(alias='_id')
    content_id: str
    quality: str
    segment: str
    date_hourly: str
    access_count: int
    traffic_factor: float = 1


class ContentSegmentCount(BaseModel, Query):
    id: BsonObjectId = Field(alias='_id')
    content_id: str
    segment: str
    quality: str
    access_count: int
