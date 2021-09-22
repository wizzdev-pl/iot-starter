import logging
import ujson

from common import config, utils
from cloud.cloud_interface import CloudProvider


class KAACloud(CloudProvider):
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
        logging.debug('cloud/Kaa_cloud.py/receive_message()')
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

    def configure_data(self) -> None:
        """
        Setup data from kaa_config file and save it to general config file
        :return: None
        """
        logging.debug("KAA_cloud/configure_data()")
        kaa_configuration = self.load_kaa_config_from_file()

        config.cfg.kaa_user = kaa_configuration.get(
            "kaa_user", config.DEFAULT_KAA_USER)

        config.cfg.kaa_password = kaa_configuration.get(
            "kaa_password", config.DEFAULT_KAA_PASSWORD)

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

        self.publish_success_topic = config.cfg.kaa_topic + '/status'
        self.publish_error_topic = config.cfg.kaa_topic + '/error'

        config.cfg.save()

    def load_kaa_config_from_file(self) -> dict:
        """
        Load configuration of KAA from file.
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
        for ind, (key, values) in enumerate(data.items()):
            # Unpack outer list and extract values to variables
            (_, value), = values
            formatted_data[key] = value

        return formatted_data

    def publish_data(self, data) -> bool:
        wireless_controller, mqtt_communicator = utils.get_wifi_and_cloud_handlers(
            sync_time=False
        )

        try:
            mqtt_communicator.subscribe(
                topic=self.publish_success_topic, callback=self.receive_message, qos=config.cfg.QOS
            )
            mqtt_communicator.subscribe(
                topic=self.publish_error_topic, callback=self.receive_message, qos=config.cfg.QOS
            )
        except OSError:
            logging.error("Error subscribing to topics with MQTT in publish_data()")
            mqtt_communicator.disconnect()
            wireless_controller.disconnect_station()
            return False

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
                return False

        mqtt_communicator.disconnect()
        wireless_controller.disconnect_station()
        return True
        