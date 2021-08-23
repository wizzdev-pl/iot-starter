import logging

import machine
import ujson
from common import config, utils
from communication import wirerless_connection_controller

from cloud.cloud_interface import CloudProvider


class ThingsBoard(CloudProvider):
    def __init__(self) -> None:
        self.publish_topic = 'v1/devices/me/telemetry'

    def receive_message(self, client, userdata, msg) -> None:
        logging.info('Topic: ' + msg.topic + '\nMessage: ' + msg.payload.decode("UTF-8"))

    def device_configuration(self, data: dict) -> int:
        """
        Configures device in the cloud. Function used as hook to web_app.
        :param data: parameters to connect to wifi.
        :return: Error code (0 - OK, 1 - Error).
        """
        logging.info("Wifi access point configuration:")

        for access_point in data:
            logging.info("Ssid: {} Password: {}".format(access_point["ssid"], access_point["password"]))

        wireless_controller = wirerless_connection_controller.get_wireless_connection_controller_instance()
        try:
            utils.connect_to_wifi(wireless_controller, data)
            logging.info(wireless_controller.sta_handler.ifconfig())
            self.configure_data()
            config.cfg.access_points = data
        except Exception as e:
            logging.error("Exception catched: {}".format(e))
            config.cfg.access_points = config.DEFAULT_ACCESS_POINTS
            config.cfg.save()
            return -1

        config.cfg.ap_config_done = True
        config.cfg.save()
        machine.reset()

        return 0

    def configure_data(self) -> None:
        """
        Setup data from thingsboard_config file and save it to general config file
        :return: None
        """
        logging.debug("ThingsBoard_config/configure_data()")
        thingsboard_configuration = self.load_thingsboard_config_from_file()

        config.cfg.thingsboard_host = thingsboard_configuration.get(
            "thingsboard_host", config.DEFAULT_THINGSBOARD_HOST)

        config.cfg.thingsboard_client_id = thingsboard_configuration.get(
            "thingsboard_client_id", config.DEFAULT_THINGSBOARD_CLIENT_ID)
            
        config.cfg.thingsboard_user = thingsboard_configuration.get(
            "thingsboard_user", config.DEFAULT_THINGSBOARD_USER)

        config.cfg.thingsboard_password = thingsboard_configuration.get(
            "thingsboard_password", config.DEFAULT_THINGSBOARD_PASSWORD)

        config.cfg.save()

    def load_thingsboard_config_from_file(self) -> dict:
        """
        Load configuration of KAA from file.
        :return: Configuration in dict.
        """
        if utils.check_if_file_exists(config.THINGSBOARD_CONFIG_PATH) == 0:
            raise Exception("Create thingsboard_config.json file first!")

        with open(config.THINGSBOARD_CONFIG_PATH, "r", encoding="utf8") as infile:
            config_dict = ujson.load(infile)

        return config_dict

    def _format_data(self, data: dict) -> dict:
        """
        Helper function for formatting data to match ThingsBoard expected input
        :param data: Data in dict to be formatted
        :return dict: Formatted data
        """
        formatted_data = {
            "ts": None,
            "values": {}
        }

        for key, values in data.items():
            # Unpack outer list and extract values to variables
            (ts, value), = values
            formatted_data['values'][key] = value
        formatted_data['ts'] = ts

        return formatted_data

    def publish_data(self, data: dict):
        wireless_controller, mqtt_communicator = utils.get_wifi_and_cloud_handlers(
            sync_time=False)

        data = self._format_data(data)

        logging.debug("data to send = {}".format(data))

        mqtt_communicator.publish_message(
            payload=data, topic=self.publish_topic, qos=config.cfg.QOS)

        mqtt_communicator.disconnect()
        wireless_controller.disconnect_station()
