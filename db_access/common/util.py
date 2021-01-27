import time
import typing as t

import pynamodb.models

from common.config import DATABASE_PREFIX, DEBUG


def get_timestamp() -> int:
    return int(round(time.time() * 1000))


def generate_table_name(basename: str) -> str:
    table_name = f"{DATABASE_PREFIX}_{basename}"
    if DEBUG:
        table_name += "_dev"
    return table_name


def generate_label(name: str) -> str:
    """ Creates nice looking string from any string provided in input """
    return " ".join([s.capitalize() for s in name.split("_")])


def create_table(model_class: t.Type[pynamodb.models.Model]):
    model_class.Meta.billing_mode = 'PAY_PER_REQUEST'  # Enables on demand capacity
    model_class.create_table(wait=True, read_capacity_units=1, write_capacity_units=1)