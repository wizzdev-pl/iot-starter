import utime
import logging
from common.utils import get_wifi_and_aws_handlers
from data_acquisition import data_acquisitor

DEFAULT_TEST_SAMPLING_INTERVAL_MS = 2000


def schedule_test_mode(_data_acquisitor: data_acquisitor.DataAcquisitor):
    wireless_controller = None
    try:
        number_measurement_to_acquire = 10  # DO NOT CHANGE IT TO LESS NUMBER
        i = 0
        while i < number_measurement_to_acquire:
            try:
                _data_acquisitor.acquire_data()
                logging.debug("Going to active sleep for {}ms. Sample number : {}".format(
                    DEFAULT_TEST_SAMPLING_INTERVAL_MS, i))
                utime.sleep_ms(DEFAULT_TEST_SAMPLING_INTERVAL_MS)
                i += 1
            except Exception as e:
                return False, "Failed to read sensor data"

        result, error_message, wireless_controller, mqtt_communicator = get_wifi_and_aws_handlers(True)
        if not result:
            logging.info("Failed to connected to AWS, {}".format(error_message))
            return result, error_message

        logging.info("Connected to AWS")
        if not mqtt_communicator.publish_message(payload=_data_acquisitor.get_data(), topic='topic/test', qos=1):
            logging.info("Failed to publish data!")
            result = (False, "Failed to publish the data")
        else:
            logging.info("Published data!")
            result = (True, "Published data")

        mqtt_communicator.disconnect()
        wireless_controller.disconnect_station()

        return result

    except BaseException as e:
        try:
            wireless_controller.disconnect_station()
        except:
            # Probably not connected ignore
            pass
        return False, "Exception occured during test {}".format(e)

