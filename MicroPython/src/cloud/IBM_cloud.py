import logging
import machine
import ujson

from common import config, utils
from communication import wirerless_connection_controller
from controller.main_controller_event import MainControllerEventType
from cloud.cloud_interface import CloudProvider


class IBMCloud(CloudProvider):
    def __init__(self) -> None:
        self.publish_success_topic = config.cfg.kaa_topic + '/status'
        self.publish_error_topic = config.cfg.kaa_topic + '/error'

    def receive_message(self, topic, msg) -> None:
        """
        Callback method for MQTT client
        :param topic: Topic of the message received encoded as bytes
        :param msg: Message received encoded as bytes
        :return: None 
        """
        logging.debug('cloud/IBM_cloud.py/receive_message()')
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
                logging.info(
                    'Operation successful with return code: {}\n'.format(msg))
        elif topic == self.publish_error_topic:
            status_code = msg['statusCode']
            reason = msg['reasonPhrase']
            logging.info('Operation failed with error code: {} - reason: {}\n'.format(
                status_code, reason
            ))
        else:
            logging.info('On topic: {} received msg: {}'.format(topic, msg))

    def device_configuration(self, data: list[dict]) -> int:
        """
        Configures device in the cloud. Function used as hook to web_app.
        :param data: parameters to connect to wifi.
        :return: Error code (0 - OK, 1 - Error).
        """
        logging.info("Wifi access point configuration:")

        for access_point in data:
            logging.info("Ssid: {} Password: {}".format(
                access_point["ssid"], access_point["password"]))

        wireless_controller = wirerless_connection_controller.get_wireless_connection_controller_instance()
        try:
            utils.connect_to_wifi(wireless_controller, data)
            logging.info(wireless_controller.sta_handler.ifconfig())
            self.configure_data()
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

    def configure_data(self) -> None:
        """
        Setup data from ibm_config file and save it to general config file
        :return: None
        """
        logging.debug("IBM_cloud/configure_data()")
        ibm_configuration = self.load_ibm_config_from_file()

        config.cfg.ibm_user = ibm_configuration.get(
            "ibm_user", config.DEFAULT_IBM_USER)

        config.cfg.ibm_password = ibm_configuration.get(
            "ibm_password", config.DEFAULT_IBM_PASSWORD)
        config.cfg.ibm_device_id = ibm_configuration.get(
            "ibm_device_id", config.DEFAULT_IBM_DEVICE_ID)
        config.cfg.ibm_organisation_id = ibm_configuration.get(
            "ibm_organisation_id", config.DEFAULT_IBM_ORGANISATION_ID)
        config.cfg.ibm_event_id = ibm_configuration.get(
            "ibm_event_id", config.DEFAULT_IBM_EVENT_ID)
        config.cfg.ibm_device_type = ibm_configuration.get(
            "ibm_device_type", config.DEFAULT_IBM_DEVICE_TYPE)
        config.cfg.ibm_topic = ibm_configuration.get(
            "ibm_topic", config.DEFAULT_IBM_TOPIC)

        config.cfg.ibm_client_id = ibm_configuration.get(
            "ibm_client_id", config.DEFAULT_IBM_CLIENT_ID
        )
        config.cfg.ibm_client_id = 'd:{}:{}:{}'.format(
            config.cfg.ibm_organisation_id, config.cfg.ibm_device_type, config.cfg.ibm_device_id
        )
        config.cfg.ibm_host = 'iot-2/evt/{}/fmt/json'.format(
            config.cfg.ibm_event_id)

        self.publish_success_topic = config.cfg.kaa_topic + '/status'
        self.publish_error_topic = config.cfg.kaa_topic + '/error'

        config.cfg.save()

    def load_ibm_config_from_file(self) -> dict:
        """
        Load configuration of KAA from file.
        :return: Configuration in dict.
        """
        if utils.check_if_file_exists(config.IBM_CONFIG_PATH) == 0:
            raise Exception("Create ibm_config.json file first!")

        with open(config.IBM_CONFIG_PATH, "r", encoding="utf8") as infile:
            config_dict = ujson.load(infile)

        return config_dict

    def _format_data(self, data: dict) -> dict:
        """
        Helper function for formatting data to match Kaa expected input
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

        result_suc_topic = mqtt_communicator.subscribe(
            topic=self.publish_success_topic, callback=self.receive_message, qos=config.cfg.QOS
        )
        result_err_topic = mqtt_communicator.subscribe(
            topic=self.publish_error_topic, callback=self.receive_message, qos=config.cfg.QOS
        )
        if not result_suc_topic or not result_err_topic:
            logging.error(
                "Error subscribing to topics with MQTT in publish_data()")

        # TODO: Add SSL connection

        data = self._format_data(data)

        logging.debug("data to send = {}".format(data))

        mqtt_communicator.publish_message(
            payload=data, topic=config.cfg.kaa_topic, qos=config.cfg.QOS
        )

        try:
            mqtt_communicator.MQTT_client.wait_msg()
        except OSError:
            # Data probably did not arrive cloud
            # Try to send data one more time up to three times
            for _ in range(3):
                mqtt_communicator.publish_message(
                    payload=data, topic=config.cfg.kaa_topic, qos=config.cfg.QOS
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
