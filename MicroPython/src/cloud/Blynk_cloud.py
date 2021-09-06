import gc
import logging
import machine
import ujson
import urequests
import utime

from common import config, utils
from common.utils import ConnectionError
from communication.wirerless_connection_controller import (
    WirelessConnectionController, get_wireless_connection_controller_instance)
from controller.main_controller_event import MainControllerEventType
from lib.BlynkLib import Blynk

from cloud.cloud_interface import CloudProvider


class Blynk_cloud(CloudProvider):
    def __init__(self) -> None:
        if not config.cfg.blynk_auth_token:
            self.configure_data()

        self.auth_token = config.cfg.blynk_auth_token
        self.temp_pin = config.cfg.blynk_temp_pin
        self.humidity_pin = config.cfg.blynk_humidity_pin
        self.blynk = Blynk(self.auth_token)

    def receive_message(self, pins: list, values: list) -> bool:
        """
        Checks if value was sent successfully to the server.
        :param pins: list of virtual pins to check
        :param values: list of values sent to the server
        :return bool: True if success, False otherwise
        """
        get_url = "http://blynk.cloud/external/api/get?token={}&v{}"
        for ind, pin in enumerate(pins):
            server_value = urequests.get(get_url.format(self.auth_token, pin))
            if round(float(server_value.text), 1) != values[ind]:
                logging.error("Error sending value to server! Sent value is: {}, received: {}".format(
                    values[ind], float(server_value.text)))
                return False

        return True

    def device_configuration(self, data: list[dict]) -> int:
        """
        Configures device in the cloud. Function used as hook to web_app.
        :param data: parameters to connect to wifi.
        :return: Error code (0 - OK, 1 - Error).
        """
        logging.debug("Wifi access point configuration:")

        for access_point in data:
            logging.info("Ssid: {} Password: {}".format(
                access_point["ssid"], access_point["password"]))

        wireless_controller = get_wireless_connection_controller_instance()
        try:
            utils.connect_to_wifi(wireless_controller, data)
            logging.info(wireless_controller.sta_handler.ifconfig())
            config.cfg.access_points = data
        except Exception as e:
            logging.error("Exception caught: {}".format(e))
            config.cfg.access_points = config.DEFAULT_ACCESS_POINTS
            config.cfg.save()
            return MainControllerEventType.ERROR_OCCURRED

        config.cfg.ap_config_done = True
        config.cfg.save()
        machine.reset()

        return 0

    def load_blynk_config_from_file(self) -> dict:
        """
        Load configuration of Blynk from file.
        :return: Configuration in dict.
        """
        if utils.check_if_file_exists(config.BLYNK_CONFIG_PATH) == 0:
            raise Exception("Create kaa_config.json file first!")

        with open(config.BLYNK_CONFIG_PATH, "r", encoding="utf8") as infile:
            config_dict = ujson.load(infile)

        return config_dict

    def configure_data(self) -> None:
        """
        Setup data from blynk_config file and save it to general config file
        :return: None
        """
        logging.debug("Blynk_cloud/configure_data()")
        blynk_configuration = self.load_blynk_config_from_file()

        config.cfg.blynk_auth_token = blynk_configuration.get(
            'blynk_auth_token', config.DEFAULT_BLYNK_AUTH_TOKEN)
        config.cfg.blynk_temp_pin = blynk_configuration.get(
            'blynk_temp_pin', config.DEFAULT_BLYNK_TEMP_PIN)
        config.cfg.blynk_humidity_pin = blynk_configuration.get(
            'blynk_humidity_pin', config.DEFAULT_BLYNK_HUMIDITY_PIN)

        config.cfg.save()

    def _format_data(self, data: dict) -> dict:
        """
        Helper function for formatting data to match Blynk expected input
        :param data: Data in dict to be formatted
        :return dict: Formatted data
        """
        formatted_data = {}
        for _, (key, values) in enumerate(data.items()):
            # Unpack outer list and extract values to variables
            (_, value), = values
            formatted_data[key] = round(value, 1)

        return formatted_data

    @staticmethod
    def wifi_connect(sync_time=False) -> WirelessConnectionController:
        """
        Connects to WiFi. It is seperate function from utils one, as Blynk doesn't use MQTT Client.
        :param sync_time: flag if time is synchronized.
        :return 
        """
        logging.debug("Blynk_cloud/wifi_connect()")

        try:
            wireless_controller = get_wireless_connection_controller_instance()
            utils.connect_to_wifi(wireless_controller,
                                  config.cfg.access_points, sync_time)

            while not wireless_controller.sta_handler.isconnected():
                utime.sleep_ms(1)
        except ConnectionError as e:
            logging.error("Error connecting to wifi with status: {}".format(e))
            try:
                wireless_controller.disconnect_station()
            except Exception:
                logging.error("Error in disconnecting WiFi controller")

        return wireless_controller

    def publish_data(self, data):
        wireless_controller = Blynk_cloud.wifi_connect(sync_time=False)

        data = self._format_data(data)
        temperature, humidity = data.get('temperature'), data.get('humidity')

        logging.debug("data to send = {}".format(data))

        self.blynk.connect()
        self.blynk.run()

        # Send data
        self.blynk.virtual_write(self.temp_pin, temperature)
        self.blynk.virtual_write(self.humidity_pin, humidity)

        gc.collect()
        utime.sleep(1)

        # Check if operation was successful
        res = self.receive_message(
            pins=[self.temp_pin, self.humidity_pin],
            values=[temperature, humidity])

        if res:
            logging.info("Operation successful!")

        wireless_controller.disconnect_station()
