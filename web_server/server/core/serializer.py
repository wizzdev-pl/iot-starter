import typing as t
import collections

import flask_restx
import flask_restx.fields as frf
import marshmallow.fields as mf
from marshmallow_pynamodb import ModelSchema

from model.base_model import Model
from common.util import create_table


class Serializer(ModelSchema):
    _api_model = None

    def __init__(self, *args, **kwargs):
        super(Serializer, self).__init__(*args, **kwargs)
        create_table(self.model())

    @property
    def api_model(self):
        if self._api_model is None:
            self._api_model = self._get_api_model()
        return self._api_model

    def loads_required(self, json_data: str, many: bool = False):
        data = self.loads(json_data=json_data, many=many).attribute_values
        if many:
            return [self._remove_additional_fields(data_entry) for data_entry in data]
        return self._remove_additional_fields(data)

    def serialize(self, obj, *, many: bool = False):
        return super(Serializer, self)._serialize(obj, many=many)

    def _remove_additional_fields(self, data: dict):
        """ Remove fields that aren't provided by user in request """
        return {k: v for k, v in data.items() if k in self.declared_fields}

    def _get_api_model(self):
        """ Map marshmallow schema into flask_restx api model """
        model_name = self.model().__name__.replace("Model", "")
        rest_attributes = collections.OrderedDict()
        for key, value in self.declared_fields.items():
            rest_attributes[key] = self.map_marshmallow_field_to_api_field(value)
        return flask_restx.Model(model_name, rest_attributes)

    @classmethod
    def model(cls) -> t.Type[Model]:
        """ Expose PynamoDB Model """
        return cls.Meta.model

    @classmethod
    def map_marshmallow_field_to_api_field(cls, marshmallow_field: mf.Field):
        if isinstance(marshmallow_field, mf.String):
            return frf.String()
        if isinstance(marshmallow_field, (mf.Raw, mf.Mapping, mf.Dict)):
            return frf.Raw()
        if isinstance(marshmallow_field, (mf.List, mf.Tuple)):
            return frf.List(cls.map_marshmallow_field_to_api_field(marshmallow_field.inner))
        if isinstance(marshmallow_field, (mf.Number, mf.Integer, mf.Decimal, mf.Int)):
            return frf.Integer()
        if isinstance(marshmallow_field, (mf.Boolean, mf.Bool)):
            return frf.Boolean()
        if isinstance(marshmallow_field, mf.Float):
            return frf.Float()
        if isinstance(marshmallow_field, mf.Date):
            return frf.Date()
        if isinstance(marshmallow_field, mf.DateTime):
            return frf.DateTime()
        if isinstance(marshmallow_field, (mf.Url, mf.URL)):
            return frf.Url()
        raise Exception(f"Cannot map {marshmallow_field} to API model field")


def serializer_factory(model_class: t.Type[Model]):
    class _Serializer(Serializer):
        is_removed = mf.Boolean(default=False)
        created_at = mf.Float(allow_none=True)

        class Meta:
            model = model_class

    return _Serializer
