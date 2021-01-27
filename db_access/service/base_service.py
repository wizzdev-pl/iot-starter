from typing import List, Type

import pynamodb
import pynamodb.exceptions

from model.base_model import Model
from common.errors import ItemNotUnique


class BaseService:
    model_class = None  # type: Type[Model]

    @classmethod
    def get(cls, hash_key, range_key=None):
        return cls.model_class.get(hash_key=hash_key, range_key=range_key)

    @classmethod
    def put(cls, **kwargs):
        item = cls.model_class(**kwargs)
        item.save()
        return item

    @classmethod
    def create_with_condition(cls, condition, error_message='', **kwargs):
        try:
            item = cls.model_class(**kwargs)
            item.save(condition=condition)
            return item
        except pynamodb.exceptions.PutError as e:
            if e.cause_response_code == 'ConditionalCheckFailedException':
                if not error_message:
                    error_message = f'Condition: "{condition}"'
                raise ItemNotUnique(error_message) from e
            else:
                raise

    @classmethod
    def get_all(cls):
        items_iterator = cls.model_class.scan()
        return [i for i in items_iterator]

    @classmethod
    def check_if_exists(cls, hash_key, range_key=None):
        try:
            cls.model_class.get(hash_key=hash_key, range_key=range_key)
            return True
        except pynamodb.exceptions.DoesNotExist:
            return False

    @classmethod
    def query(cls, *args, **kwargs):
        return cls.model_class.query(*args, **kwargs)

    @classmethod
    def get_latest(cls, hash_key, reverse=True, range_key_condition=None, limit=5):
        items_iterator = cls.model_class.query(
            hash_key=hash_key,
            range_key_condition=range_key_condition,
            scan_index_forward=False,
            limit=limit)
        items_list = [item for item in items_iterator]
        if reverse:
            items_list = items_list[::-1]
        return items_list

    @classmethod
    def scan(cls, reverse=True, **kwargs):
        items_iterator = cls.model_class.scan(**kwargs)
        return [item for item in items_iterator][::-1]

    @classmethod
    def write_batch(cls, items_data: List[dict]):
        """ Create multiple items in batch operation, but without condition checking """
        with cls.model_class.batch_write() as batch:
            items = [cls.model_class(**d) for d in items_data]
            for item in items:
                batch.save(item)
