import logging

import machine
import ujson
from common import config, utils
from communication import wirerless_connection_controller
from controller.main_controller_event import (MainControllerEvent,
                                              MainControllerEventType)

from cloud.cloud_interface import CloudProvider


class ThingsBoard(CloudProvider):
    def __init__(self) -> None:
        self.rpc_response_topic = 'v1/devices/me/rpc/response/'
        self.rpc_request_topic = 'v1/devices/me/rpc/request/'
        self.publish_topic = 'v1/devices/me/telemetry'

    # def receive_message(self, topic, msg) -> None:
    #     """
    #     Callback method for MQTT client
    #     :param topic: Topic of the message received encoded as bytes
    #     :param msg: Message received encoded as bytes
    #     :return: None
    #     """
    #     logging.debug('cloud/Things_cloud.py/receive_message()')
    #     topic = topic.decode()

    #     # Check if msg is in json format, if not decode as str
    #     if b'{' in msg and b'}' in msg:
    #         msg = ujson.loads(msg)
    #     else:
    #         msg = msg.decode()

    #     if topic == self.rpc_response_topic:
    #         if msg == '':
    #             logging.info('Operation successful\n')
    #         else:
    #             logging.info('Operation successful with return code: {}\n'.format(msg))
    #     elif topic == self.rpc_request_topic:
    #         status_code = msg['statusCode']
    #         reason = msg['reasonPhrase']
    #         logging.info('Operation failed with error code: {} - reason: {}\n'.format(
    #             status_code, reason
    #         ))
    #     else:
    #         logging.info('On topic: {} received msg: {}'.format(topic, msg))

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
            #self.configure_data()
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
        Setup data from thingsboard_config file and save it to general config file
        :return: None
        """
        logging.debug("ThingsBoard_config/configure_data()")
        thingsboard_configuration = self.load_thingsboard_config_from_file()
        
        config.cfg.thingsboard_host = thingsboard_configuration.get(
            "thingsboard_host", config.DEFAULT_THINGSBOARD_HOST)

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
        formatted_data = {}
        for ind, (key, values) in enumerate(data.items()):
            # Unpack outer list and extract values to variables
            (_, value), = values
            formatted_data[key] = value
        
        return formatted_data

    def publish_data(self, data):
        wireless_controller, mqtt_communicator = utils.get_wifi_and_cloud_handlers(
            sync_time=False
        )

        # result_suc_topic = mqtt_communicator.subscribe(
        #     topic=self.rpc_response_topic, callback=self.receive_message, qos=config.cfg.QOS
        # )
        # result_err_topic = mqtt_communicator.subscribe(
        #     topic=self.rpc_request_topic, callback=self.receive_message, qos=config.cfg.QOS
        # )
        # if not result_suc_topic or not result_err_topic:
        #     logging.error("Error subscribing to topics with MQTT in publish_data()")

        # TODO: Certificates?

        data = self._format_data(data)

        logging.debug("data to send = {}".format(data))
        
        mqtt_communicator.publish_message(payload=data, topic=self.publish_topic, qos=config.cfg.QOS)

        try:
            mqtt_communicator.MQTT_client.wait_msg()
        except OSError:
            # Data probably did not arrive cloud
            # Try to send data one more time up to three times
            for _ in range(3):
                mqtt_communicator.publish_message(
                    payload=data, topic=self.publish_topic, qos=config.cfg.QOS
                )
                try:
                    mqtt_communicator.MQTT_client.wait_msg()
                except OSError:
                    # Failed again, trying up to three times
                    continue
                break
            else:
                logging.debug(
                    "Tried to send data three times, failed! Aborting current measurement."
                )


        mqtt_communicator.disconnect()
        wireless_controller.disconnect_station()