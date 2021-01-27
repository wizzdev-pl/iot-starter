import datetime
import string
import random
import os

from service.device_service import DeviceService
from service.measurement_service import MeasurementService, MeasurementTypeService

os.environ["DATABASE_HOST"] = "http://localhost:4567"

# Please consider using batch_write when you are trying to add more than 20 devices once
dummy_devices_count = 10
dummy_devices_group_count = 3
dummy_measurement_type_count = 3
dummy_measurement_count_per_device = 1000


# Measurement types
dummy_measurement_types = []
for j in range(dummy_measurement_type_count):
    measurement_type_name = f"measurement_type_{string.ascii_letters[j:j + 2]}"
    dummy_measurement_types.append(measurement_type_name)
    MeasurementTypeService.create_measurement_type_if_not_exist(name=measurement_type_name)

# Devices
for i in range(dummy_devices_count):
    print(f"{i * 100 // dummy_devices_count}%")
    # Devices
    device_id = f"dev_{(string.ascii_letters[i] * 3).upper()}"
    device_group_name = f"group_{string.ascii_letters[(i % 3) + 1] * 3}"
    try:
        DeviceService.create_device(
            device_id=device_id,
            description=f"Description for {device_id}",
            device_group=device_group_name,
            device_type="Fictitious")
    except:
        pass
    dummy_measurements = []
    # Measurement
    start_measurement = random.randint(1, 9)
    for j in range(dummy_measurement_count_per_device):
        date = datetime.datetime.utcnow() - datetime.timedelta(minutes=10 * (dummy_measurement_count_per_device - j))
        measurement_type = dummy_measurement_types[j % dummy_measurement_type_count]
        value = start_measurement + (random.randint(0, 8)) - 4
        MeasurementService.create_measurement(
            device_id=device_id, value=value,
            timestamp=int(round(date.timestamp() * 1000)), measurement_type=measurement_type
        )
