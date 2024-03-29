import gc
import logging
import ujson
import urequests

from common import config, utils
from controller.main_controller_event import MainControllerEventType
from cloud.cloud_interface import CloudProvider


class ThingsBoardCloud(CloudProvider):
    def __init__(self) -> None:
        self.request_topic = 'v1/devices/me/rpc/request/+'
        self.publish_topic = 'v1/devices/me/telemetry'

    def api_configuration(self) -> None:
        """
        Configure device in API (get JWT, get device ID, create attributes)
        :return: None
        """
        logging.debug("Api configuration")
        logging.info(
            "Allocated bytes on heap before gc {}".format(gc.mem_alloc()))
        gc.collect()
        logging.info(
            "Allocated bytes on heap after gc {}".format(gc.mem_alloc()))

        config.cfg.thingsboard_jwt_token = self.authorization_request()

        if config.cfg.thingsboard_jwt_token:
            config.cfg.thingsboard_device_id = self.get_device_id(
                config.cfg.thingsboard_jwt_token)

            if config.cfg.thingsboard_device_id:

                if self.create_attributes(config.cfg.thingsboard_jwt_token, config.cfg.thingsboard_device_id) != MainControllerEventType.ERROR_OCCURRED:
                    config.cfg.thingsboard_attributes_exists = True

        config.cfg.save()

    def authorization_request(self) -> str:
        """
        Register your device in cloud. It takes password and login from thingsboard_config.json
        :return: JSON Web Token
        """
        logging.debug("Authorization request function")
        headers = {
            'Content-Type': 'application/json'
        }

        url = 'http://{}:{}/api/auth/login'.format(
            config.cfg.thingsboard_host, config.DEFAULT_THINGSBOARD_PORT)

        data = {
            "username": config.cfg.thingsboard_username,
            "password": config.cfg.thingsboard_password
        }

        logging.debug('username: {}, password: {}'.format(
            config.cfg.thingsboard_username, config.cfg.thingsboard_password))
        data = ujson.dumps(data)

        try:
            response = urequests.post(url, headers=headers, data=data)
            logging.debug("Authorized!")
        except IndexError as e:
            logging.error("No internet connection: {}".format(e))
            return ""
        except Exception as e:
            logging.error("Failed to authorize in API {}".format(e))
            return ""

        if response.status_code != '200' and response.status_code != 200:
            logging.error(response.text)
            return ""

        response_dict = response.json()
        jwt_token = response_dict.get("token")
        return jwt_token

    def get_device_id(self, jwt_token) -> str:
        """
        Get ID of the previously specified device
        :return: device ID
        """
        logging.debug("Getting device id...")

        url = 'http://{}:{}/api/tenant/devices?pageSize=100&page=0'.format(
            config.cfg.thingsboard_host, config.DEFAULT_THINGSBOARD_PORT)

        headers = {
            'x-authorization': 'Bearer {}'.format(jwt_token),
            'content-type': 'application/json'
        }

        response = urequests.get(url=url, headers=headers)

        if response.status_code == 200:
            response_dict = response.json()
            response_data = response_dict.get('data')

            for data in response_data:
                if data.get('name') == config.cfg.thingsboard_device_name:
                    device_dict = data.get('id')
                    device_id = device_dict.get('id')
                    logging.debug("Got device ID!")
                    return device_id

            logging.debug("Could not find any device named: {}".format(
                config.cfg.thingsboard_device_name))
            return ""
        else:
            logging.error("Error while getting device ID! Status code: {}".format(
                response.status_code))
            return ""

    def create_attributes(self, jwt_token, device_id) -> int:
        """
        Create new attributes for device
        :return: Error code (0 - OK, ERROR_OCCURRED = 99 - Error)
        """
        logging.debug("Adding new attributes")

        url = 'http://{}:{}/api/plugins/telemetry/DEVICE/{}/SERVER_SCOPE'.format(
            config.cfg.thingsboard_host, config.DEFAULT_THINGSBOARD_PORT, device_id)

        headers = {
            'x-authorization': 'Bearer {}'.format(jwt_token),
            'content-type': 'application/json'
        }

        data_raw = {
            "SleepTime": config.DEFAULT_DATA_PUBLISHING_PERIOD_MS / 1000
        }

        data = ujson.dumps(data_raw)
        response = urequests.post(url=url, headers=headers, data=data)

        if response.status_code == 200:
            logging.debug("Added new attributes!")
            return 0
        else:
            logging.error("Error while adding new attributes! Error code: {}".format(
                response.status_code))
            return MainControllerEventType.ERROR_OCCURRED

    def get_sleep_time(self, jwt_token, device_id) -> int:
        """
        Acquire attributes provided in dashboard.
        :return: Sleep time (config.cfg.data_publishing_period_in_ms)
        """
        logging.debug("Acquisition of new attributes...")

        url = 'http://{}:{}/api/plugins/telemetry/DEVICE/{}/values/attributes/SERVER_SCOPE'.format(
            config.cfg.thingsboard_host, config.DEFAULT_THINGSBOARD_PORT, device_id)
        headers = {
            'x-authorization': 'Bearer {}'.format(jwt_token),
            'content-type': 'application/json'
        }

        response = urequests.get(url=url, headers=headers)

        if response.status_code == 200:
            response_dict = response.json()

            for item in response_dict:
                if item.get('key') == 'SleepTime' and \
                        item.get('value') != config.cfg.data_publishing_period_in_ms / 1000:
                    logging.debug("Got new attributes")
                    logging.debug(
                        "New data will be applied at the next wake-up call")
                    return item.get('value')

            logging.debug("Did not find any new attributes")
            return 0
        else:
            logging.error("Wrong device ID!")
            return 0

    def receive_message(self, topic, msg) -> None:
        """
        Callback method for MQTT client
        :param topic: Topic of the message received encoded as bytes
        :param msg: Message received encoded as bytes
        :return: None
        """
        logging.debug('cloud/Things_cloud.py/receive_message()')
        topic = topic.decode()

        # Check if msg is in json format, if not decode as str
        if b'{' in msg and b'}' in msg:
            msg = ujson.loads(msg)
        else:
            msg = msg.decode()

        if topic == True:
            logging.info('Operation successful\n')
        else:
            logging.info('Operation failed\n')

    def configure_data(self) -> None:
        """
        Setup data from thingsboard_config file and save it to general config file
        :return: None
        """
        logging.debug("ThingsBoard_config/configure_data()")
        thingsboard_configuration = self.load_thingsboard_config_from_file()

        config.cfg.thingsboard_host = thingsboard_configuration.get(
            "thingsboard_host", config.DEFAULT_THINGSBOARD_HOST)

        config.cfg.thingsboard_device_client_id = thingsboard_configuration.get(
            "thingsboard_device_client_id", config.DEFAULT_THINGSBOARD_DEVICE_CLIENT_ID)

        config.cfg.thingsboard_device_username = thingsboard_configuration.get(
            "thingsboard_device_username", config.DEFAULT_THINGSBOARD_DEVICE_USERNAME)

        config.cfg.thingsboard_device_password = thingsboard_configuration.get(
            "thingsboard_device_password", config.DEFAULT_THINGSBOARD_DEVICE_PASSWORD)

        config.cfg.thingsboard_device_name = thingsboard_configuration.get(
            "thingsboard_device_name", config.DEFAULT_THINGSBOARD_DEVICE_NAME)

        config.cfg.thingsboard_username = thingsboard_configuration.get(
            "thingsboard_username", config.DEFAULT_THINGSBOARD_USERNAME)

        config.cfg.thingsboard_password = thingsboard_configuration.get(
            "thingsboard_password", config.DEFAULT_THINGSBOARD_PASSWORD)

        config.cfg.save()

    def load_thingsboard_config_from_file(self) -> dict:
        """
        Load configuration of ThingsBoard from file.
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

    def publish_data(self, data: dict) -> bool:
        wireless_controller, mqtt_communicator = utils.get_wifi_and_cloud_handlers(
            sync_time=False)

        result_request_topic = mqtt_communicator.subscribe(
            topic=self.request_topic, callback=self.receive_message, qos=config.cfg.QOS)

        if result_request_topic:
            logging.debug("Connected to ThingsBoard!")
        else:
            logging.debug("Error while connecting to ThingsBoard!")

        if config.cfg.thingsboard_attributes_exists:
            sleep_time = self.get_sleep_time(
                config.cfg.thingsboard_jwt_token, config.cfg.thingsboard_device_id)
            if sleep_time >= 30:
                config.cfg.data_publishing_period_in_ms = sleep_time*1000
                config.cfg.save()
            else:
                logging.debug(
                    "Sleep time is lower than allowed ({}seconds).".format(sleep_time))
        else:
            self.api_configuration()

        data = self._format_data(data)

        logging.debug("data to send = {}".format(data))

        mqtt_communicator.publish_message(
            payload=data, topic=self.publish_topic, qos=config.cfg.QOS)

        mqtt_communicator.disconnect()
        wireless_controller.disconnect_station()
        return True
        