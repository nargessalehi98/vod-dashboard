from datetime import datetime
from typing import Literal, Optional, List

from pydantic import validator
from pydantic.main import BaseModel

from config.models import Admin, Content, Provider, Genre, File, Person
from config.utils import datetime_now


class UploadPictureOutputSerializer(BaseModel):
    secret_key: str
    upload_url: str


class AddSeriesSerializer(BaseModel):
    type: str = 'NewSeries'
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
    poster_id: str = ""

    @validator('provider_id')
    def validate_provider(cls, provider_id, values):
        admin = Admin.get_one(_id=values.get('admin_id'))
        if not admin.is_super_admin and provider_id is not None:
            raise ValueError('this user is not allowed to set provider_id ')
        if provider_id is None and not admin.is_super_admin:
            return values.get('admin_id')
        return provider_id

    @validator('IMDB_link')
    def validate_IMDB_link(cls, IMDB_link):
        if "www.imdb.com" not in IMDB_link:
            raise ValueError('IMDB link is not valid')
        return IMDB_link


class UploadPictureSerializer(BaseModel):
    source_id: str
    type: Literal['Avatar', 'Logo', 'Poster', 'Image']
    extension: Literal['JPEG', 'JPG', 'PNG']
    size: int
    name: str

    @validator('source_id')
    def validate_source_id(cls, source_id):
        if Content.get_one(_id=source_id) is None and Provider.get_one(_id=source_id) is None \
                and Admin.get_one(_id=source_id) is None:
            raise ValueError('content is not valid')
        return source_id


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


class UploadContentSerializer(BaseModel):
    # series
    series_id: Optional[str]
    season: Optional[int]
    episode: Optional[int]
    # movies
    actors_id: Optional[list]
    # both
    title: str
    summery: str
    language: Optional[str]
    genre: Optional[List[str]]
    age: Optional[Literal['Adults', 'Children', 'Both']]
    director_id: Optional[str]
    producer_id: Optional[str]
    persons_id: Optional[List[str]]
    IMDB_link: Optional[str]
    tags: Optional[List[str]]
    publish_datetime: Optional[datetime] = datetime_now()
    admin_id: str
    provider_id: Optional[str]
    type: Literal['Movie', 'SeriesEpisode']

    @validator('IMDB_link')
    def validate_IMDB_link(cls, IMDB_link):
        if "www.imdb.com" not in IMDB_link:
            raise ValueError('IMDB link is not valid')
        return IMDB_link

    @validator('provider_id')
    def validate_provider(cls, provider_id, values):
        admin = Admin.get_one(_id=values.get('admin_id'))
        if not admin.is_super_admin:
            raise ValueError('this user is not allowed to set provider_id ')
        if provider_id is None and admin.is_super_admin:
            return values.get('admin_id')
        return provider_id

    @validator('type')
    def validate_type(cls, type, values):
        if type == 'SeriesEpisode':
            if values.get('season') is None or values.get('episode') is None or values.get('series_id') is None:
                raise ValueError('series needs season and episode')
            if values.get('director_id') is not None or values.get('producer_id') is not None:
                raise ValueError('series dont need director or producer')
            if values.get('genre') is not None or values.get('age') is not None:
                raise ValueError('series dont need genre or age')
            if values.get('actors_ids') is not None or values.get('language') is not None:
                raise ValueError('no need to actors_id')
        if type == 'Movie':
            if values.get('season') is not None or values.get('episode') is not None:
                raise ValueError('movies dont needs season and episode')
            if values.get('genre') is None or values.get('age') is None or values.get('language') is None:
                raise ValueError('movies need genre and age and language')
            if values.get('director_id') is None or values.get('producer_id') is None or values.get(
                    'actors_id') is None:
                raise ValueError('movies need director and producer and actor')
        return type


class DeletePictureSerializer(BaseModel):
    type: Literal['Avatar', 'Logo', 'Poster', 'Image']
    picture_id: str
    source_id: str

    @validator('picture_id')
    def picture_id_validator(cls, picture_id, values):
        file = File.get_one(_id=picture_id)
        if file is None:
            raise ValueError('picture id is not valid')
        if values.get('type') != file.type:
            raise ValueError('type is not valid')
        return picture_id

    @validator('source_id')
    def source_id_validator(cls, source_id, values):
        if values.get('type') == 'Avatar':
            admin = Admin.get_one(_id=source_id)
            if admin is None:
                admin = Person.get_one(_id=source_id)
            if admin is None or admin.avatar_id != values.get('picture_id'):
                raise ValueError('Avatar and source dose not math')

        if values.get('type') == 'Logo':
            provider = Provider.get_one(_id=source_id)
            if provider is None or provider.logo_file_id != values.get('picture_id'):
                raise ValueError('Logo and source dose not math')

        if values.get('type') == 'Poster':
            content = Content.get_one(_id=source_id)
            if content is None or content.poster_id != values.get('picture_id'):
                raise ValueError('Poster and source dose not math')

        if values.get('type') == 'Image':
            content = Content.get_one(_id=source_id)
            if content is None or values.get('picture_id') not in content.images_id:
                raise ValueError('Image and source dose not math')
        return source_id
