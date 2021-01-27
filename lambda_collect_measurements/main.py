import logging
import os

import sentry_sdk

from db_access.service.measurement_service import MeasurementService


def main(*args, **kwargs):
    # init sentry
    sentry_dsn = os.environ.get('SENTRY')
    if sentry_dsn:
        sentry_sdk.init(sentry_dsn, environment=os.environ.get("MODE", "undefined"))
        sentry_sdk.add_breadcrumb(args[0])

    payload = args[0]
    device_id = payload['client_id']

    # Add measurements to database
    for measurement_type, measurement_raws in payload['data'].items():
        measurements = []
        try:
            for timestamp, value in measurement_raws:
                measurements.append({
                    'device_id': device_id,
                    'timestamp': timestamp,
                    'value': value,
                    'measurement_type': measurement_type
                })
            MeasurementService.create_measurements(measurements)
        except Exception as exception:
            logging.exception(f"Exception occurred while adding measurements to database: {exception} "
                              f"\n Inputs: {measurement_type}, {measurement_raws}")
            sentry_sdk.capture_exception(exception)
