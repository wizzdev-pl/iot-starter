import logging
import machine

from common import config, utils
from communication.wirerless_connection_controller import get_wireless_connection_controller_instance
from controller.main_controller_event import MainControllerEventType


class Providers:
    AWS = "AWS"
    KAA = "KAA"
    THINGSBOARD = "THINGSBOARD"
    BLYNK = "BLYNK"
    IBM = "IBM"

class CloudProvider:
    def device_configuration(self, wifi_credentials: list[dict]) -> int:
        """
        Configures device in the cloud. Function used as hook to web_app.
        :param wifi_credentials: parameters to connect to wifi.
        :return: Error code (0 - OK, 1 - Error).
        """
        logging.debug("Wifi access point configuration:")

        for access_point in wifi_credentials:
            logging.info("Ssid: {} Password: {}".format(
                access_point["ssid"], access_point["password"]))

        wireless_controller = get_wireless_connection_controller_instance()
        try:
            utils.connect_to_wifi(wireless_controller, wifi_credentials)
            logging.info(wireless_controller.sta_handler.ifconfig())
            config.cfg.access_points = wifi_credentials
            self.configure_data()
            wireless_controller.disconnect_station()
        except Exception as e:
            logging.error("Exception caught: {}".format(e))
            config.cfg.access_points = config.DEFAULT_ACCESS_POINTS
            config.cfg.save()
            return MainControllerEventType.ERROR_OCCURRED

        config.cfg.ap_config_done = True
        config.cfg.save()
        machine.reset()

        return 0
    
    def configure_data(self):
        pass

    def publish_data(self, data):
        """
        Publish data to the cloud
        :param data: data to be sent to cloud
        :return: None
        """
        pass
