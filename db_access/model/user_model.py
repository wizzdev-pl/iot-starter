from pynamodb.attributes import UnicodeAttribute

from common.config import IOT_AWS_REGION, DATABASE_HOST
from common.util import generate_table_name
from model.base_model import AuditModel


class UserLoginModel(AuditModel):
    class Meta:
        table_name = generate_table_name("iot_users")
        region = IOT_AWS_REGION
        host = DATABASE_HOST

    username = UnicodeAttribute(hash_key=True)
    password = UnicodeAttribute()
