import logging
import machine
import urequests

from ujson import loads, dumps, load
from common import config, utils
from communication import wirerless_connection_controller
from controller.main_controller_event import MainControllerEvent, MainControllerEventType
from cloud.cloud_interface import CloudProvider


class ThingsBoard(CloudProvider):
    def __init__(self) -> None:
        self.rpc_response_topic = 'v1/devices/me/rpc/response/'
        self.rpc_request_topic = 'v1/devices/me/rpc/request/+'

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
            return -1

        config.cfg.ap_config_done = True
        config.cfg.save()
        machine.reset()

        return 0
    
    def authorization_request(self) -> str:
        """
        Register your device in cloud. It takes password and login from thingsboard_config.json
        :return: JSON Web Token
        """
        logging.debug("Authorization request function")
        headers = {
            'Content-Type': 'application/json'
        }
        
        url = 'http://{}:{}/api/auth/login'.format(config.cfg.thingsboard_host, 8080)

        data = {
            "username": config.cfg.thingsboard_username,
            "password": config.cfg.thingsboard_password
        }

        logging.debug('username: {}, password: {}'.format(config.cfg.thingsboard_username, config.cfg.thingsboard_password))
        data = dumps(data)

        try:
            response = urequests.post(url, headers=headers,data=data)
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

    def get_sleep_time(self, jwt_token) -> int:
        """
        Acquire attributes provided in dashboard.
        """
        logging.debug("Acquisition of new attributes...")
        
        url = 'http://{}:{}/api/plugins/telemetry/DEVICE/{}/values/attributes/SERVER_SCOPE'.format(
            config.cfg.thingsboard_host, 8080, 'DEVICE ID HERE')
        headers = {
            'x-authorization': 'Bearer {}'.format(jwt_token), 
            'content-type': 'application/json'
        }

        get_dict = urequests.get(url=url, headers=headers).text
        conv_to_dict = loads(get_dict)
        for item in conv_to_dict:
            if item['key'] == 'SleepTime':
                sleep_time_dict = item

        if sleep_time_dict:
            logging.debug("Got new attributes")
            return sleep_time_dict['value']
        else:
            logging.debug("Did not find any new attributes")
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
            msg = loads(msg)
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
            config_dict = load(infile)

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

        jwt_token = self.authorization_request()
        
        if jwt_token:
            config.cfg.data_publishing_period_in_ms = self.get_sleep_time(jwt_token)*1000
            config.cfg.save()

        result_request_topic = mqtt_communicator.subscribe(
            topic=self.rpc_request_topic, callback=self.receive_message, qos=config.cfg.QOS)

        if result_request_topic:
            logging.debug("Connected to ThingsBoard!")
        else:
            logging.debug("Error while connecting to ThingsBoard!")

        data = self._format_data(data)

        logging.debug("data to send = {}".format(data))
        
        mqtt_communicator.publish_message(payload=data, topic=config.DEFAULT_THINGSBOARD_PUBLISH_TOPIC, qos=config.cfg.QOS)

        mqtt_communicator.disconnect()
        wireless_controller.disconnect_station()
