import bson
from typing import Tuple, overload
from config.utils import to_object_id, query_logger
from config.settings import db  # # # Do Not Delete This Import
from bson import ObjectId  # # # Do Not Delete This Import
import datetime  # # # Do Not Delete This Import


class Query:
    # # # Main

    @classmethod
    @query_logger
    def get_one(cls, _data: dict = None, /, **kwargs):
        """ example: \nUser.get_one(_id=_id) """
        if _data is None:
            _data = {}
        if '_id' in _data:
            _data['_id'] = to_object_id(_data['_id'])
        if '_id' in kwargs:
            kwargs['_id'] = to_object_id(kwargs['_id'])
        obj = eval(f'db.{cls.__name__}.find_one(_data | kwargs)')
        return cls(**obj) if obj else None

    @classmethod
    @query_logger
    def count(cls, _data: dict = None, /, **kwargs) -> int:
        """
        example:
            User.count({'state': {'$eq': 'Confirmed'}}, name='ali', age=24)
        """
        if _data is None:
            _data = {}

        _data = {k: v for k, v in _data.items() if v not in [None]}
        kwargs = {k: v for k, v in kwargs.items() if v not in [None]}
        if '_id' in _data:
            _data['_id'] = to_object_id(_data['_id'])
        if '_id' in kwargs:
            kwargs['_id'] = to_object_id(kwargs['_id'])
        return eval(f'db.{cls.__name__}.count_documents(_data | kwargs)')

    @classmethod
    @query_logger
    def list(cls, _data: dict = None, /, **kwargs):
        """
        example:
            User.list({'state': {'$eq': 'Confirmed'}}, name='ali', age=24)
        """
        if _data is None:
            _data = {}
        _data = {k: v for k, v in _data.items() if v not in [None]}
        kwargs = {k: v for k, v in kwargs.items() if v not in [None]}
        if '_id' in _data:
            _data['_id'] = to_object_id(_data['_id'])
        if '_id' in kwargs:
            kwargs['_id'] = to_object_id(kwargs['_id'])
        return eval(f'db.{cls.__name__}.find(_data | kwargs)')

    @classmethod
    @query_logger
    def create(cls, **kwargs) -> bson.objectid.ObjectId:
        """ example: \nUser.create(name='ali', age=24, ...) """
        return eval(f'db.{cls.__name__}.insert_one({kwargs})')

    @classmethod
    @query_logger
    def delete_one(cls, **kwargs):
        """ example: \nUser.delete_one(_id=_id) """
        if '_id' in kwargs:
            kwargs['_id'] = to_object_id(kwargs['_id'])
        result = eval(f'db.{cls.__name__}.delete_one(kwargs)')
        return bool(result.deleted_count)

    @classmethod
    @query_logger
    def delete_many(cls, **kwargs) -> int:
        """ example: \nUser.delete_many(name='ali') """
        result = eval(f'db.{cls.__name__}.delete_many(kwargs)')
        return result.deleted_count

    @query_logger
    def update(self, **kwargs) -> dict:
        _filter = {'_id': self._id}
        _update = {'$set': kwargs}
        return eval(f'db.{self.__class__.__name__}.update_one(_filter, _update)')

    @classmethod
    @query_logger
    def update_variable(cls, filter, update):
        """ example: \nUser.update_one({'_id': _id}, {'name':'ali'}) """
        if '_id' in filter:
            filter['_id'] = to_object_id(filter['_id'])
        return eval(f'db.{cls.__name__}.update_one({filter}, {update})')

    @classmethod
    @query_logger
    def update_one(cls, filter, **kwargs) -> dict:
        """ example: \nUser.update_one({'_id': _id}, name='ali') """
        if '_id' in filter:
            filter['_id'] = to_object_id(filter['_id'])
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        _update = {'$set': kwargs}
        return eval(f'db.{cls.__name__}.update_one({filter}, {_update})')

    @classmethod
    @query_logger
    def update_many(cls, filter, **kwargs) -> dict:
        """ example: \nUser.update_many({'name': 'mohsen'}, name='ali') """
        _update = {'$set': kwargs}
        return eval(f'db.{cls.__name__}.update_many(filter, _update)')

    @classmethod
    @query_logger
    def increment(cls, filter, **kwargs):
        """
        example:
            User.increment({'priority': {'$gt': ad.priority}}, score=1)
        * it will increment score by 1
        """
        _update = {'$inc': kwargs}
        return eval(f'db.{cls.__name__}.update_many({filter}, {_update})')

    @classmethod
    @query_logger
    def get_or_create(cls, **kwargs) -> Tuple[bool, any]:
        obj = cls.get_one(**kwargs)
        if obj:
            return False, obj
        else:
            return True, cls.create(**kwargs)

    @classmethod
    @query_logger
    def aggregate(cls, match_list, group_list, project, pre_sort, sort, skip, limit):
        """
        example:
            User.aggregate( [X, Y, Z ,...], date ,20, 10,[group1 , group2 ,...] )
        * it will increment score by 1
        """
        pipline = []
        if match_list:
            match_list = {'$match': {'$and': match_list}}
            if pre_sort:
                pre_sort = {'$sort': {f'{pre_sort}': -1}}
                pipline.append(pre_sort)
            pipline = [match_list, *group_list]
        if project:
            project = {'$project': project}
            pipline.append(project)
        if sort:
            sort = {'$sort': {f'{sort}': -1}}
            pipline.append(sort)
        if skip:
            skip = {'$skip': skip}
            pipline.append(skip)
        if limit:
            limit = {'$limit': limit}
            pipline.append(limit)
        return eval(f'db.{cls.__name__}.aggregate(pipline)')
