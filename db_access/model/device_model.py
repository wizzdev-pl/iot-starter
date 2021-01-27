import typing as t

from pynamodb.attributes import UnicodeAttribute, JSONAttribute

from common.config import IOT_AWS_REGION, DATABASE_HOST
from common.util import generate_table_name, create_table
from model.base_model import AuditModel


class DeviceTypeModel(AuditModel):
    class Meta:
        table_name = generate_table_name("iot_device_types")
        region = IOT_AWS_REGION
        host = DATABASE_HOST

    device_type = UnicodeAttribute(hash_key=True)
    description = UnicodeAttribute(null=True)


class DeviceGroupModel(AuditModel):
    class Meta:
        table_name = generate_table_name("iot_device_groups")
        region = IOT_AWS_REGION
        host = DATABASE_HOST

    device_group = UnicodeAttribute(hash_key=True)
    description = UnicodeAttribute(null=True)


class DeviceModel(AuditModel):
    class Meta:
        table_name = generate_table_name("iot_devices")
        region = IOT_AWS_REGION
        host = DATABASE_HOST

    device_id = UnicodeAttribute(hash_key=True)
    description = UnicodeAttribute(null=True)
    device_type = UnicodeAttribute(default="default")
    device_group = UnicodeAttribute(default="default")
    settings = JSONAttribute(default={})
