import logging
import machine
import ujson

from common import config, utils
from communication import wirerless_connection_controller
from controller.main_controller_event import MainControllerEventType
from cloud.cloud_interface import CloudProvider


class IBMCloud(CloudProvider):
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
        config.cfg.ibm_organization_id = ibm_configuration.get(
            "ibm_organization_id", config.DEFAULT_IBM_ORGANIZATION_ID)
        config.cfg.ibm_event_id = ibm_configuration.get(
            "ibm_event_id", config.DEFAULT_IBM_EVENT_ID)
        config.cfg.ibm_device_type = ibm_configuration.get(
            "ibm_device_type", config.DEFAULT_IBM_DEVICE_TYPE)

        config.cfg.ibm_client_id = 'd:{}:{}:{}'.format(
            config.cfg.ibm_organization_id, config.cfg.ibm_device_type, config.cfg.ibm_device_id)
        config.cfg.ibm_topic = 'iot-2/evt/{}/fmt/json'.format(
            config.cfg.ibm_event_id)
        config.cfg.ibm_host = '{}.messaging.internetofthings.ibmcloud.com'.format(
            config.cfg.ibm_organization_id)

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

    def publish_data(self, data) -> bool:
        wireless_controller, mqtt_communicator = utils.get_wifi_and_cloud_handlers(
            sync_time=False
        )

        data = self._format_data(data)

        logging.debug("data to send = {}".format(data))

        message_published = mqtt_communicator.publish_message(
            payload=data, topic=config.cfg.ibm_topic, qos=config.cfg.QOS
        )
        if not message_published:
            for _ in range(3):
                message_published = mqtt_communicator.publish_message(
                    payload=data, topic=config.cfg.ibm_topic, qos=config.cfg.QOS
                )
                logging.debug(
                    "Trying to send data again"
                )
                if message_published:
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