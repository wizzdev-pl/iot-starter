import logging
from random import randint

import machine
import ujson
from common import config, utils
from communication import wirerless_connection_controller
from controller.main_controller_event import (MainControllerEvent,
                                              MainControllerEventType)
from utime import time

from cloud.cloud_interface import CloudProvider


class KAA_cloud(CloudProvider):
    def __init__(self) -> None:
        # TODO: Only needed for checking if there are any messages
        self.publish_success_topic = config.cfg.kaa_success_topic
        self.publish_error_topic = config.cfg.kaa_error_topic

    def receive_message(self, topic, msg) -> None:
        """
        Callback method for MQTT client
        :param topic: Topic of the message received encoded as bytes
        :param msg: Message received encoded as bytes
        :return: None 
        """
        topic = topic.decode()

        # Check if msg is in json format, if not decode as str
        if b'{' in msg and b'}' in msg:
            msg = ujson.loads(msg)
        else:
            msg = msg.decode()

        if topic == self.publish_success_topic:
            if msg == '':
                logging.info('Operation successful\n')
            else:
                logging.info('Operation successful with return code: {}\n'.format(msg))
        elif topic == self.publish_error_topic:
            status_code = msg['statusCode']
            reason = msg['reasonPhrase']
            logging.info('Operation failed with error code: {} - reason: {}\n'.format(
                status_code, reason
            ))
        else:
            logging.info('On topic: {} received msg: {}'.format(topic, msg))

    def device_configuration(self, data: dict) -> int:
        """
        Configures device in the cloud. Function used as hook to web_app.
        :param data: parameters to connect to wifi.
        :return: Error code (0 - OK, 1 - Error).
        """
        ssid = data['ssid']
        password = data['password']

        config.cfg.ssid = ssid
        config.cfg.password = password
        config.cfg.save()

        logging.info(
            "Wifi config. Wifi ssid {} Wifi password {}".format(ssid, password))

        wireless_controller = wirerless_connection_controller.get_wireless_connection_controller_instance()
        try:
            utils.connect_to_wifi(wireless_controller)
            logging.info(wireless_controller.sta_handler.ifconfig())
            self.configure_data()
        except Exception as e:
            logging.error("Exception catched: {}".format(e))
            event = MainControllerEvent(MainControllerEventType.ERROR_OCCURRED)
            self.add_event(event)
            return 1

        config.cfg.ap_config_done = True
        config.cfg.save()
        machine.reset()

        return 0

    def configure_data(self) -> None:
        """
        Setup data from kaa_config file and save it to general config file
        :return: None
        """
        logging.debug("KAA_cloud/configure_data()")
        kaa_configuration = self.load_kaa_config_from_file()
        
        config.cfg.kaa_app_version = kaa_configuration.get(
            "kaa_app_version", config.DEFAULT_KAA_APP_VERSION)
        
        config.cfg.kaa_endpoint = kaa_configuration.get(
            "kaa_endpoint", config.DEFAULT_KAA_APP_VERSION)

        # Update in case app_version of kaa_endpoint changed
        config.cfg.kaa_topic = 'kp1/{}/dcx/{}/json/{}'.format(
            config.cfg.kaa_app_version, 
            config.cfg.kaa_endpoint, 
            config.cfg.mqqt_request_id
        )

        config.cfg.save()

    def load_kaa_config_from_file(self) -> dict:
        """
        Load configuration of AWS from file.
        :return: Configuration in dict.
        """
        if utils.check_if_file_exists(config.KAA_CONFIG_PATH) == 0:
            raise Exception("Create kaa_config.json file first!")

        with open(config.KAA_CONFIG_PATH, "r", encoding="utf8") as infile:
            config_dict = ujson.load(infile)

        return config_dict

    def _format_data(self, data: dict) -> dict:
        """
        Helper function for formatting data to match Kaa expected input
        :param data: Data in dict to be formatted
        :return dict: Formatted data
        """
        formatted_data = {}
        for key, values in data.items():
            # Unpack outer list and extract values to variables
            (_, value), = values
            # !!! UNCOMMENT ONLY FOR DEBUGGING
            if value == -99:
                # random.seed(time())
                value = randint(10, 40)
            # !!! UNCOMMENT ONLY FOR DEBUGGING
            formatted_data[key] = value
        
        return formatted_data

    def publish_data(self, data):
        wireless_controller, mqtt_communicator = utils.get_wifi_and_cloud_handlers(
            sync_time=False
        )

        result = mqtt_communicator.set_callback(self.receive_message)
        if not result:
            logging.error(
                "Error subscribing to topics with MQTT in publish_data()")

        # TODO: Certificates?

        data = self._format_data(data)

        logging.debug("data to send = {}".format(data))
        result = mqtt_communicator.publish_message(
            payload=data, topic=config.cfg.kaa_topic, qos=config.cfg.QOS
        )

        # TODO: Do we need to wait here for confirmation from receive_message method?
        if not result:
            logging.error(
                "Does publish return result for KAA?? (MQTT in publish_data())")

        mqtt_communicator.disconnect()
        wireless_controller.disconnect_station()