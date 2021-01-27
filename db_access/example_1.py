""" A simple example demonstrating basic library usage:
- how to create a device (in database, don't confuse with creating 'thing' with certifivates)
- how to add measurements
- how to obtain measurements for devices
"""

import time

from service.device_service import DeviceService
from service.measurement_service import MeasurementService
from view.device_view import DeviceView

if not DeviceService.check_if_device_exists('dev_p_1'):
    DeviceService.create_device(device_id='dev_p_1', description='long description of dev_p_1')
    for i in range(5):
        MeasurementService.create_measurement(device_id='dev_p_1', value=4 + i + i % 3 - i // 5)
        time.sleep(0.1)
else:
    print(f'dev_p_1 device timestamp: {DeviceService.get("dev_p_1").creation_timestamp}')


if not DeviceService.check_if_device_exists('dev_p_2'):
    DeviceService.create_device(device_id='dev_p_2', description='long description of dev_p_2')
    for i in range(5):
        MeasurementService.create_measurement(device_id='dev_p_2', value=2100 + i)
        time.sleep(0.1)
else:
    print(f'dev_p_2 device timestamp: {DeviceService.get("dev_p_2").creation_timestamp}')


if not DeviceService.check_if_device_exists('dev_p_3'):
    DeviceService.create_device(device_id='dev_p_3', description='long description of dev_p_3')
else:
    print(f'dev_p_3 device timestamp: {DeviceService.get("dev_p_3").creation_timestamp}')



# get some data
devices_txt = [d.device_id for d in DeviceService.get_all()]
print(f'Device list: {devices_txt}')

newest_measurements_2 = DeviceView.get_newest_measurements_for_device(device_id='dev_p_2')
print(f'newest_measurements for device dev_p_2: {newest_measurements_2}')

dev_with_newest_measurements = DeviceView.get_all_devices_with_last_measurement()
txt = [f'device {device_id}: {value}' for device_id, value in dev_with_newest_measurements.items()]
print(f'newest_measurements for devices: {txt}')
