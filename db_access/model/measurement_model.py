from pynamodb.attributes import UnicodeAttribute, NumberAttribute

from common.config import IOT_AWS_REGION, DATABASE_HOST
from common.util import generate_table_name, create_table
from model.base_model import AuditModel, Model


class MeasurementTypeModel(AuditModel):
    class Meta:
        table_name = generate_table_name("iot_measurement_types")
        region = IOT_AWS_REGION
        host = DATABASE_HOST

    name = UnicodeAttribute(hash_key=True)
    label = UnicodeAttribute()
    unit = UnicodeAttribute(default="", null=True)
    description = UnicodeAttribute(null=True)
    priority = NumberAttribute(null=True, default=0)


class MeasurementModel(Model):
    class Meta:
        table_name = generate_table_name("iot_measurements")
        region = IOT_AWS_REGION
        host = DATABASE_HOST

    device_id = UnicodeAttribute(hash_key=True)
    timestamp = NumberAttribute(range_key=True)
    measurement_type = UnicodeAttribute()
    value = NumberAttribute()
