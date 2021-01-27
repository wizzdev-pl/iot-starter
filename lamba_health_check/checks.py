import time

import requests

from db_access import MeasurementService, DeviceService


FOUR_HOURS_AGO = time.time() - (60 * 60 * 4)
FOUR_DAYS_AGO = time.time() - (60 * 60 * 24 * 4)


def was_any_measurement_sent_recently(break_point_timestamp: float = FOUR_HOURS_AGO):
    measurements = MeasurementService.model_class.scan(limit=1)
    measurement = measurements.next()
    return measurement.timestamp > break_point_timestamp

def is_visualization_okay(url: str):
    with requests.get(url) as response:
        return response.status_code == 200