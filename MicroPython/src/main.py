from machine import reset, reset_cause, wake_reason, HARD_RESET, PWRON_RESET, SOFT_RESET, PIN_WAKE, lightsleep
import logging
import _thread

from controller.main_controller import MainController
from controller.main_controller_event import MainControllerEventType, MainControllerEvent
from common import config, utils


def main():
    logging.debug("=== MAIN START ===")

    # Increase stack size per thread this increases micropython recursion depth
    _thread.stack_size(8192 * 3)

    # Read and parse configuration from config.json
    utils.init()

    controller = MainController()

    # Check if configuration via access point has to be started
    if not config.cfg.ap_config_done or wake_reason() == PIN_WAKE:
        logging.debug("AP_DONE: {}, wake_reason: {}".format(config.cfg.ap_config_done, wake_reason()))
        logging.debug("Access points saved:")
        for ap in config.cfg.access_points:
            logging.debug("SSID: {} Password: {}".format(ap["ssid"], ap["password"]))
        if config.cfg.access_points != config.DEFAULT_ACCESS_POINTS:
            logging.debug("Access points aren't default. Try to connect")
        else:
            logging.debug("=== Entering configuration mode ===")

            event = MainControllerEvent(MainControllerEventType.CONFIGURE_ACCESS_POINT)
            controller.add_event(event)

    logging.debug("Main loop")
    # If the device is powered on, then actual time from NTP server must be downloaded

    if reset_cause() == HARD_RESET or reset_cause() == PWRON_RESET or reset_cause() == SOFT_RESET:
        event = MainControllerEvent(MainControllerEventType.TEST_CONNECTION)
        controller.add_event(event)

    # Print actual time
    event = MainControllerEvent(MainControllerEventType.PRINT_TIME)
    controller.add_event(event)

    # Read temperature and humidity from the sensor and return the data as JSON
    event = MainControllerEvent(MainControllerEventType.GET_SENSOR_DATA)
    controller.add_event(event)

    # Connect to WIFI and publish JSON with data to cloud via MQTT
    event = MainControllerEvent(MainControllerEventType.PUBLISH_DATA)
    controller.add_event(event)

    # Good night!
    event = MainControllerEvent(MainControllerEventType.GO_TO_SLEEP, callback=None,
                                ms=config.cfg.data_publishing_period_in_ms)
    controller.add_event(event)

    controller.perform()


if __name__ == '__main__':
    main()
