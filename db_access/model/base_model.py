import typing as t

import pynamodb.models
import pynamodb.attributes as attributes

from common.util import get_timestamp


class Model(pynamodb.models.Model):
    class Meta:
        abstract = True


class AuditModel(Model):
    class Meta:
        abstract = True

    is_removed = attributes.BooleanAttribute(default=False)
    created_at = attributes.NumberAttribute(default=get_timestamp())
    modified_at = attributes.NumberAttribute(default=get_timestamp())

    def save(self, condition=None) -> t.Dict[str, t.Any]:
        self.modified_at = get_timestamp()
        return super().save(condition)

    def safe_delete(self):
        self.is_removed = True
        return self.save()
