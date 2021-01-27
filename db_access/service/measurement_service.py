import typing as t

import pynamodb.exceptions

import common.errors
from common.util import get_timestamp, generate_label
from service.base_service import BaseService
from model.measurement_model import MeasurementModel, MeasurementTypeModel


class MeasurementService(BaseService):
    model_class = MeasurementModel

    @classmethod
    def create_measurement(cls, device_id: str, value: int or float, measurement_type: str,
                           timestamp: int = None) -> MeasurementModel:
        result = cls.create_with_condition(
            condition=MeasurementModel.timestamp.does_not_exist(),
            error_message=f'Measurement with specified timestamp ({timestamp})'
                          f' already exists for device with id "{device_id}"!',
            device_id=device_id,
            value=value,
            measurement_type=measurement_type,
            timestamp=timestamp or get_timestamp(),
        )
        MeasurementTypeService.create_measurement_type_if_not_exist(
            name=measurement_type,
            label=generate_label(measurement_type),
            description="Created automatically during adding measurements"
        )
        return result

    @classmethod
    def create_measurements(cls, measurements: t.List[dict]):
        cls.write_batch(measurements)
        measurements_types = set([measurement.get('measurement_type') for measurement in measurements])
        for measurement_type in measurements_types:
            MeasurementTypeService.create_measurement_type_if_not_exist(
                name=measurement_type,
                label=generate_label(measurement_type),
                description="Created automatically during adding measurements"
            )


class MeasurementTypeService(BaseService):
    model_class = MeasurementTypeModel

    @classmethod
    def create_measurement_type(cls,
                                name: str,
                                label: str = None,
                                description: str = None,
                                unit: str = "",
                                priority: int = 0) -> MeasurementTypeModel:
        return cls.create_with_condition(
            name=name,
            label=label,
            description=description,
            unit=unit,
            priority=priority,
            condition=cls.model_class.name.does_not_exist(),
            error_message=f'Measurement Type with specified id ("{name}") already exists!'
        )

    @classmethod
    def create_measurement_type_if_not_exist(cls,
                                             name: str,
                                             label: str = None,
                                             description: str = None,
                                             unit: str = "",
                                             priority: int = 0) -> MeasurementTypeModel:
        try:
            return cls.create_measurement_type(name=name, label=label or generate_label(name),
                                               description=description, priority=priority, unit=unit)
        except (pynamodb.exceptions.PutError, common.errors.ItemNotUnique):
            pass
