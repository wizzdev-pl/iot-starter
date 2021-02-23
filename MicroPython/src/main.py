import time

from machine import Pin, reset, reset_cause, wake_reason, HARD_RESET, PWRON_RESET, SOFT_RESET, PIN_WAKE
import logging
import _thread
from controller.main_controller import MainController
from controller.main_controller_event import MainControllerEventType, MainControllerEvent
from power_management.deepsleep_handler import power_save, publish_to_aws, check_connection_to_aws
from common import config
from common.utils import time_print
from data_acquisition.data_acquisitor import DataAcquisitor


def main():
    logging.debug("=== MAIN START ===")

    # Increase stack size per thread this increases micropython recursion depth
    _thread.stack_size(8192*2)
    
    # Read and parse configuration from config.json
    config.init()

    # Check if configuration via access point has to be started
    if not config.cfg.ap_config_done or wake_reason() == PIN_WAKE:
        logging.debug("AP_DONE: {}, wake_reason: {}".format(config.cfg.ap_config_done, wake_reason()))
        logging.debug("SSID: {}, Password: {}".format(config.cfg.ssid, config.cfg.password))
        if config.cfg.ssid != 'ssid' and config.cfg.password != 'password':
            logging.debug("SSID and password aren't default. Try to connect")
            pass
        else:
            logging.debug("=== Entering configuration mode ===")

            controller = MainController()
            event = MainControllerEvent(MainControllerEventType.CONFIGURE_ACCESS_POINT)
            controller.process_event(event)
            controller.perform()

            config.cfg.ap_config_done = True
            config.save()
            reset()

    logging.debug("Main loop")
    # If the device is powered on, then actual time from NTP server must be downloaded
    if reset_cause() == HARD_RESET or reset_cause() == PWRON_RESET or reset_cause() == SOFT_RESET:
        check_connection_to_aws()

    # Print actual time
    time_print()

    # Read temperature and humidity from the sensor and return the data as JSON
    data_acquisitor = DataAcquisitor()
    result = data_acquisitor.acquire_temp_humi()

    # Connect to WIFI and publish JSON with data to AWS via MQTT
    publish_to_aws(result)

    # Good night!
    power_save(config.cfg.data_publishing_period_in_ms)


if __name__ == '__main__':
    main()
