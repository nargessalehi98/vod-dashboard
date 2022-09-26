import hashlib
from typing import Optional, Literal, List

from bson import ObjectId
from bson.errors import BSONError
from pydantic import BaseModel, Field

from config.queries import Query
from datetime import datetime, timedelta


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


class AccessGroup(BaseModel, Query):
    id: BsonObjectId = Field(alias='_id')
    title: str
    accesses: list


class Admin(BaseModel, Query):
    id: BsonObjectId = Field(alias='_id')
    username: str
    password: str
    email: Optional[str]
    title: Optional[str]
    avatar_url: Optional[str]
    access_group: Optional[List]
    last_access_time: Optional[datetime]
    status: Optional[Literal['Active', 'Deactive']]

    @property
    def _id(self):
        return ObjectId(self.id) if self.id else None

    def check_password(self, raw_password: str):
        return self.password == hashlib.md5(raw_password.encode('utf-8')).hexdigest()

    @classmethod
    def make_password(cls, raw_password):
        return hashlib.md5(raw_password.encode('utf-8')).hexdigest()


class Provider(BaseModel, Query):
    id: BsonObjectId = Field(alias='_id')
    name: str
    dc_id: str  # data center id which is in DataCenterServer table
    logo_file_id: str  # file id which is in File table
    url: str  # Relative URL which becomes complete by dc download_url  in ServerInfo table
    provider_id: str


class Access(BaseModel, Query):
    id: BsonObjectId = Field(alias='_id')
    access: Literal[
        'AddAdmin', 'ModifyAdmin', ' ViewAdmin', 'EditDashboardProfile', 'ViewAccessGroup', 'AddAccessGroup',
        'AddProvider', 'ModifyProvider', 'ViewProvider']


class DataCenterInfo(BaseModel, Query):
    id: BsonObjectId = Field(alias='_id')
    download_url: str
    upload_url: str


class File(BaseModel, Query):
    id: BsonObjectId = Field(alias='_id')
    dc_id: str
    status: Literal['Draft', 'Done']
    type: Literal['Avatar']
    download_url: str


class Content(BaseModel, Query):
    id: BsonObjectId = Field(alias='_id')
    title: str
    director: str
    producer: str
    summery: Optional[str]
    actors: list
    language: str
    genre: Optional[List[Literal[
        'Action', 'Comedy', 'Horror', 'Sci-Fi', 'Western', 'Romance', 'Thriller', 'Fantasy', 'Historical', 'Crime',
        'Mystery', 'Drama', 'Animation', 'Experimental', 'Musical', 'War', 'Biographical']]]
    IMDB_link: Optional[str]
    age: Literal['G', 'PG', 'PG-13', 'R', 'NC-17']
    status: Literal[
        'Uploading', 'AwaitingConfirmation', 'QueuingPublication', 'Published', 'Deleted', 'Rejected', 'ReadyPublish']
    status_description: Optional[str]
    tags: Optional[list]
    poster_id: Optional[str]
    images_ids: Optional[list]
    comments: Optional[Literal['']]
    length: Optional[timedelta]
    publish_datetime: Optional[datetime]


class ContentAccessLog(BaseModel, Query):
    id: BsonObjectId = Field(alias='_id')
    content_id: str
    provider_id: str
    date_hourly: str  # "2022-10-12-23"
    isp_name: Literal['MCI', 'MTN', 'Other']
    accessed_bytes: int
    traffic_factor: float  # 1/traffic_factor per day


class TotalTraffic(BaseModel, Query):
    id: BsonObjectId = Field(alias='_id')
    date_hourly: str
    isp_name: Literal['MCI', 'MTN', 'Other']
    accessed_bytes: int
    traffic_factor: float


class ContentAccessCountLog(BaseModel, Query):
    id: BsonObjectId = Field(alias='_id')
    content_id: str
    quality: str
    segment: str
    date_hourly: str
    access_count: int
    traffic_factor: float


class ContentSegmentCount(BaseModel, Query):
    content_id: str
    segment: str
    quality: str
    access_count: int
