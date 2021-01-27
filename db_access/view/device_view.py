from typing import Dict, Union, List

from common.errors import ItemDoesNotExist
from model.measurement_model import MeasurementModel
from service.device_service import DeviceService
from service.measurement_service import MeasurementService
from view.base_view import BaseView


class DeviceView(BaseView):

    @classmethod
    def get_all_devices_with_last_measurement(cls) -> Dict[str, Union[float, None]]:
        measurements_with_value = {}
        for name, measurement in cls.get_all_devices_with_last_measurement_and_time().items():
            measurements_with_value[name] = measurement.value if measurement else None
        return measurements_with_value

    @classmethod
    def get_all_devices_with_last_measurement_and_time(cls) -> Dict[str, Union[MeasurementModel, None]]:
        devices_with_measurement = {}
        devices = DeviceService.get_all()
        for device_id in devices:
            device_id = device_id.device_id
            newest_measurements = cls.get_newest_measurements_for_device(
                device_id=device_id,
                max_number_of_measurements=1)
            if not newest_measurements:
                newest_measurement_value = None
            else:
                newest_measurement_value = newest_measurements[0]
            devices_with_measurement[device_id] = newest_measurement_value
        return devices_with_measurement

    @classmethod
    def get_newest_measurements_for_device(cls, device_id, max_number_of_measurements=3) -> List[MeasurementModel]:
        if not DeviceService.check_if_device_exists(device_id=device_id):
            raise ItemDoesNotExist(f'Device with ID "{device_id}" does not exist!')

        return MeasurementService.get_latest(hash_key=device_id, limit=max_number_of_measurements)

    @staticmethod
    def get_measurements_for_device_for_time_range(device_id,
                                                   start_timestamp,
                                                   end_timestamp,
                                                   max_number_of_measurements=10):
        return MeasurementService.scan(
            limit=max_number_of_measurements,
            filter_condition=(
                    (MeasurementModel.device_id == device_id)
                    &
                    (MeasurementModel.timestamp.between(start_timestamp, end_timestamp))
            ))
