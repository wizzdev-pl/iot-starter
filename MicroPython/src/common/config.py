from ujson import dump, load
from lib import logging

from common import utils
from communication.wirerless_connection_controller import \
    get_mac_address_as_string


cfg = None

DEFAULT_CLOUD_PROVIDER = ''

DEFAULT_ACCESS_POINTS = []

# Connection
DEFAULT_DATA_PUBLISHING_PERIOD_MS = 120000
DEFAULT_WIFI_TIMEOUT = 5000
DEFAULT_MQTT_PORT = 1883
DEFAULT_MQTT_REQUEST_ID = 42
DEFAULT_MQTT_PORT_SSL = 8883
DEFAULT_MQTT_TIMEOUT = 60
DEFAULT_THINGSBOARD_PORT = 8080
DEFAULT_QOS = 1
DEFAULT_TESTED_CONNECTION_CLOUD = False
DEFAULT_WIFI_CONNECTION_FAILED = False

DEFAULT_PRIV_KEY = ""
DEFAULT_CERT_PEM = ""
DEFAULT_CERT_CA = ""

# Sensors
DEFAULT_SENSOR_MEASUREMENT_PIN = 27
DEFAULT_SENSOR_POWER_PIN = 26
DEFAULT_SENSOR_TYPE = "DHT22"
DEFAULT_SENSOR_SDA_PIN = 21
DEFAULT_SENSOR_SCL_PIN = 22

# Other
DEFAULT_AP_CONFIG_DONE = False
DEFAULT_NTP_SYNCHRONIZED = False
DEFAULT_CONFIGURATION_AFTER_FIRST_POWER_ON_DONE = False
DEFAULT_API_URL = ""
DEFAULT_API_LOGIN = ""
DEFAULT_API_PASSWORD = ""
DEFAULT_DEVICE_UID = ''

# Paths
CERTIFICATES_DIR = "/certificates"
CONFIG_FILE_PATH = 'config.json'

# AWS stuff
DEFAULT_AWS_ENDPOINT = 'topic/data'
DEFAULT_AWS_CLIENT_ID = 'default_id'
DEFAULT_AWS_TOPIC = 'topic/data'
AWS_CONFIG_PATH = "/resources/aws_config.json"
AWS_API_AUTHORIZATION_URL = 'Auth/login'
AWS_API_CONFIG_URL = "Device/"
AWS_THING_NAME_PREFIX = "ESP32"
KEY_PATH = "{}/{}".format(CERTIFICATES_DIR, "AWS.private_key")
CERTIFICATE_PATH = "{}/{}".format(CERTIFICATES_DIR, "AWS.certificate")
CA_CERTIFICATE_PATH = "{}/{}".format(CERTIFICATES_DIR, "AWS.ca_certificate")

DEFAULT_JSON_HEADER = {'Content-Type': 'application/json'}

# KAA stuff
KAA_CONFIG_PATH = "/resources/kaa_config.json"
DEFAULT_KAA_KPC_HOST = "mqtt.cloud.kaaiot.com"
DEFAULT_KAA_APP_VERSION = ""
DEFAULT_KAA_ENDPOINT = ""
DEFAULT_KAA_USER = ""
DEFAULT_KAA_PASSWORD = ""
DEFAULT_KAA_TOPIC = 'kp1/{}/dcx/{}/json/{}'.format(
    DEFAULT_KAA_APP_VERSION, DEFAULT_KAA_ENDPOINT, DEFAULT_MQTT_REQUEST_ID
)

# ThingsBoard stuff
THINGSBOARD_CONFIG_PATH = '/resources/thingsboard_config.json'
DEFAULT_THINGSBOARD_HOST = 'localhost'
DEFAULT_THINGSBOARD_DEVICE_CLIENT_ID = ''
DEFAULT_THINGSBOARD_DEVICE_USERNAME = ''
DEFAULT_THINGSBOARD_DEVICE_PASSWORD = ''
DEFAULT_THINGSBOARD_DEVICE_NAME = ''
DEFAULT_THINGSBOARD_USERNAME = "tenant@thingsboard.org"
DEFAULT_THINGSBOARD_PASSWORD = "tenant"
DEFAULT_THINGSBOARD_JWT_TOKEN = ''
DEFAULT_THINGSBOARD_DEVICE_ID = ''
DEFAULT_THINGSBOARD_ATTRIBUTES_EXISTS = False

# Blynk stuff
BLYNK_CONFIG_PATH = 'resources/blynk_config.json'
DEFAULT_BLYNK_AUTH_TOKEN = ''
DEFAULT_BLYNK_TEMPERATURE_PIN = -1
DEFAULT_BLYNK_HUMIDITY_PIN = -1

# IBM stuff
IBM_CONFIG_PATH = "/resources/ibm_config.json"
DEFAULT_IBM_DEVICE_ID = ""
DEFAULT_IBM_USER = "use-token-auth"
DEFAULT_IBM_ORGANIZATION_ID = ""
DEFAULT_IBM_PASSWORD = ""
DEFAULT_IBM_EVENT_ID =""
DEFAULT_IBM_DEVICE_TYPE = "IoTStarter"
DEFAULT_IBM_TOPIC = 'iot-2/evt/{}/fmt/json'.format(
     DEFAULT_IBM_EVENT_ID
 )
#DEFAULT_IBM_TOPIC = 'iot-2/evt/topi/fmt/json'

DEFAULT_IBM_HOST = '{}.messaging.internetofthings.ibmcloud.com'.format(DEFAULT_IBM_ORGANIZATION_ID)
#'tf2veq.messaging.internetofthings.ibmcloud.com'
#DEFAULT_IBM_CLIENT_ID = 'd:tf2veq:IoTStarter:IoTStarter-test'
DEFAULT_IBM_CLIENT_ID = 'd:{}:{}:{}'.format(
    DEFAULT_IBM_ORGANIZATION_ID, DEFAULT_IBM_DEVICE_TYPE, DEFAULT_IBM_DEVICE_ID
)

class ESPConfig:
    """
    Class to save, write and handle configuration of ESP device.
    Creates config.json file, where is written data about wifi connection, certificates, credentials etc.
    """

    def __init__(self):
        """
        ESPConfig constructor.
        """
        logging.debug("ESPConfig.__init__()")

        self.cloud_provider = DEFAULT_CLOUD_PROVIDER

        self.access_points = DEFAULT_ACCESS_POINTS

        # Connection
        self.data_publishing_period_in_ms = DEFAULT_DATA_PUBLISHING_PERIOD_MS
        self.wifi_timeout = DEFAULT_WIFI_TIMEOUT
        self.mqtt_port = DEFAULT_MQTT_PORT
        self.mqqt_request_id = DEFAULT_MQTT_REQUEST_ID
        self.mqtt_port_ssl = DEFAULT_MQTT_PORT_SSL
        self.mqtt_timeout = DEFAULT_MQTT_TIMEOUT
        self.QOS = DEFAULT_QOS
        self.tested_connection_cloud = DEFAULT_TESTED_CONNECTION_CLOUD
        self.wifi_connection_failed = DEFAULT_WIFI_CONNECTION_FAILED

        self.private_key = DEFAULT_PRIV_KEY
        self.cert_pem = DEFAULT_CERT_PEM
        self.cert_ca = DEFAULT_CERT_CA

        # Sensors
        self.sensor_measurement_pin = DEFAULT_SENSOR_MEASUREMENT_PIN
        self.sensor_power_pin = DEFAULT_SENSOR_POWER_PIN
        self.sensor_type = DEFAULT_SENSOR_TYPE
        self.sensor_sda_pin = DEFAULT_SENSOR_SDA_PIN
        self.sensor_scl_pin = DEFAULT_SENSOR_SCL_PIN

        # Other
        self.ap_config_done = DEFAULT_AP_CONFIG_DONE
        self.ntp_synchronized = DEFAULT_NTP_SYNCHRONIZED
        self.configuration_after_first_power_on_done = DEFAULT_CONFIGURATION_AFTER_FIRST_POWER_ON_DONE

        # AWS
        self.aws_endpoint = DEFAULT_AWS_ENDPOINT
        self.aws_client_id = DEFAULT_AWS_CLIENT_ID
        self.aws_topic = DEFAULT_AWS_TOPIC
        self.api_url = DEFAULT_API_URL
        self.api_login = DEFAULT_API_LOGIN
        self.api_password = DEFAULT_API_PASSWORD
        self.device_uid = ""

        # KAA
        self.kaa_user = DEFAULT_KAA_USER
        self.kaa_password = DEFAULT_KAA_PASSWORD
        self.kaa_endpoint = DEFAULT_KAA_ENDPOINT
        self.kaa_app_version = DEFAULT_KAA_APP_VERSION
        self.kaa_topic = DEFAULT_KAA_TOPIC

        # ThingsBoard
        self.thingsboard_host = DEFAULT_THINGSBOARD_HOST
        self.thingsboard_device_client_id = DEFAULT_THINGSBOARD_DEVICE_CLIENT_ID
        self.thingsboard_device_username = DEFAULT_THINGSBOARD_DEVICE_USERNAME
        self.thingsboard_device_password = DEFAULT_THINGSBOARD_DEVICE_PASSWORD
        self.thingsboard_device_name = DEFAULT_THINGSBOARD_DEVICE_NAME
        self.thingsboard_username = DEFAULT_THINGSBOARD_USERNAME
        self.thingsboard_password = DEFAULT_THINGSBOARD_PASSWORD
        self.thingsboard_jwt_token = DEFAULT_THINGSBOARD_JWT_TOKEN
        self.thingsboard_device_id = DEFAULT_THINGSBOARD_DEVICE_ID
        self.thingsboard_attributes_exists = DEFAULT_THINGSBOARD_ATTRIBUTES_EXISTS

        # Blynk
        self.blynk_auth_token = DEFAULT_BLYNK_AUTH_TOKEN
        self.blynk_temperature_pin = DEFAULT_BLYNK_TEMPERATURE_PIN
        self.blynk_humidity_pin = DEFAULT_BLYNK_HUMIDITY_PIN

        # IBM
        self.ibm_host = DEFAULT_IBM_HOST
        self.ibm_device_id = DEFAULT_IBM_DEVICE_ID
        self.ibm_user = DEFAULT_IBM_USER
        self.ibm_organization_id = DEFAULT_IBM_ORGANIZATION_ID
        self.ibm_password =  DEFAULT_IBM_PASSWORD
        self.ibm_event_id = DEFAULT_IBM_EVENT_ID
        self.ibm_device_type = DEFAULT_IBM_DEVICE_TYPE
        self.ibm_topic = DEFAULT_IBM_TOPIC
        self.ibm_client_id = DEFAULT_IBM_CLIENT_ID



    def load_from_file(self) -> None:
        """
        Load configuration of ESP from file.
        :return: None
        """
        logging.debug("ESPConfig.load_from_file()")
        config_file_exists = True
        if not utils.check_if_file_exists(CONFIG_FILE_PATH):
            with open(CONFIG_FILE_PATH, "w", encoding="utf8") as file:
                config_file_exists = False
                empty_config = {}
                self.device_uid = get_mac_address_as_string()
                dump(empty_config, file)

        with open(CONFIG_FILE_PATH, "r", encoding="utf8") as infile:
            config_dict = load(infile)

            self.cloud_provider = config_dict.get(
                'cloud_provider', DEFAULT_CLOUD_PROVIDER)

            self.access_points = config_dict.get(
                'access_points', DEFAULT_ACCESS_POINTS)

            # Connection
            self.data_publishing_period_in_ms = config_dict.get(
                'data_publishing_period_ms', DEFAULT_DATA_PUBLISHING_PERIOD_MS)
            self.wifi_timeout = config_dict.get(
                'wifi_connection_timeout', DEFAULT_WIFI_TIMEOUT)
            self.mqtt_port = config_dict.get('mqtt_port', DEFAULT_MQTT_PORT)
            self.mqqt_request_id = config_dict.get(
                'mqtt_request_id', DEFAULT_MQTT_REQUEST_ID)
            self.mqtt_port_ssl = config_dict.get(
                'mqtt_port_ssl', DEFAULT_MQTT_PORT_SSL)
            self.mqtt_timeout = config_dict.get(
                'mqtt_timeout', DEFAULT_MQTT_TIMEOUT)
            self.QOS = config_dict.get('QOS', DEFAULT_QOS)
            self.tested_connection_cloud = config_dict.get(
                'tested_connection_cloud', DEFAULT_TESTED_CONNECTION_CLOUD)
            self.wifi_connection_failed = config_dict.get(
                'wifi_connection_failed', DEFAULT_WIFI_CONNECTION_FAILED)

            self.private_key = config_dict.get('private_key', DEFAULT_PRIV_KEY)
            self.cert_pem = config_dict.get('cert_pem', DEFAULT_CERT_PEM)
            self.cert_ca = config_dict.get('cert_ca', DEFAULT_CERT_CA)

            # Sensors
            self.sensor_measurement_pin = config_dict.get(
                'sensor_measurement_pin', DEFAULT_SENSOR_MEASUREMENT_PIN)
            self.sensor_power_pin = config_dict.get(
                'sensor_power_pin', DEFAULT_SENSOR_POWER_PIN)
            self.sensor_type = config_dict.get(
                'sensor_type', DEFAULT_SENSOR_TYPE)
            self.sensor_sda_pin = config_dict.get(
                'sensor_sda_pin', DEFAULT_SENSOR_SDA_PIN)
            self.sensor_scl_pin = config_dict.get(
                'sensor_scl_pin', DEFAULT_SENSOR_SCL_PIN)

            # Other
            self.ap_config_done = config_dict.get(
                'AP_config_done', DEFAULT_AP_CONFIG_DONE)
            self.configuration_after_first_power_on_done = \
                config_dict.get('configuration_after_first_power_on_done',
                                DEFAULT_CONFIGURATION_AFTER_FIRST_POWER_ON_DONE)

            # AWS
            self.aws_endpoint = config_dict.get(
                'aws_endpoint', DEFAULT_AWS_ENDPOINT)
            self.aws_client_id = config_dict.get(
                'client_id', DEFAULT_AWS_CLIENT_ID)
            self.aws_topic = config_dict.get('topic', DEFAULT_AWS_TOPIC)

            # KAA
            self.kaa_user = config_dict.get('kaa_user', DEFAULT_KAA_USER)
            self.kaa_password = config_dict.get(
                'kaa_password', DEFAULT_KAA_PASSWORD)
            self.kaa_endpoint = config_dict.get(
                'kaa_endpoint', DEFAULT_KAA_ENDPOINT)
            self.kaa_app_version = config_dict.get(
                'kaa_app_version', DEFAULT_KAA_APP_VERSION)
            self.kaa_topic = config_dict.get('kaa_topic', DEFAULT_KAA_TOPIC)

            # ThingsBoard
            self.thingsboard_host = config_dict.get(
                'thingsboard_host', DEFAULT_THINGSBOARD_HOST)
            self.thingsboard_device_client_id = config_dict.get(
                'thingsboard_device_client_id', DEFAULT_THINGSBOARD_DEVICE_CLIENT_ID)
            self.thingsboard_device_username = config_dict.get(
                'thingsboard_device_username', DEFAULT_THINGSBOARD_DEVICE_USERNAME)
            self.thingsboard_device_password = config_dict.get(
                'thingsboard_device_password', DEFAULT_THINGSBOARD_DEVICE_PASSWORD)
            self.thingsboard_device_name = config_dict.get(
                'thingsboard_device_name', DEFAULT_THINGSBOARD_DEVICE_NAME)
            self.thingsboard_username = config_dict.get(
                'thingsboard_username', DEFAULT_THINGSBOARD_USERNAME)
            self.thingsboard_password = config_dict.get(
                'thingsboard_password', DEFAULT_THINGSBOARD_PASSWORD)
            self.thingsboard_jwt_token = config_dict.get(
                'thingsboard_jwt_token', DEFAULT_THINGSBOARD_JWT_TOKEN)
            self.thingsboard_device_id = config_dict.get(
                'thingsboard_device_id', DEFAULT_THINGSBOARD_DEVICE_ID)
            self.thingsboard_attributes_exists = config_dict.get(
                'thingsboard_attributes_exists', DEFAULT_THINGSBOARD_ATTRIBUTES_EXISTS)

            # Blynk
            self.blynk_auth_token = config_dict.get(
                'blynk_auth_token', DEFAULT_BLYNK_AUTH_TOKEN)
            self.blynk_temperature_pin = config_dict.get(
                'blynk_temperature_pin', DEFAULT_BLYNK_TEMPERATURE_PIN)
            self.blynk_humidity_pin = config_dict.get(
                'blynk_humidity_pin', DEFAULT_BLYNK_HUMIDITY_PIN)

            # IBM
            self.ibm_host = config_dict.get(
                'ibm_host', DEFAULT_IBM_HOST)
            self.ibm_device_id = config_dict.get(
                'ibm_device_id', DEFAULT_IBM_DEVICE_ID)
            self.ibm_user = config_dict.get(
                'ibm_user', DEFAULT_IBM_USER)
            self.ibm_organization_id =  config_dict.get(
                'ibm_organization_id', DEFAULT_IBM_ORGANIZATION_ID)
            self.ibm_password = config_dict.get(
                'ibm_password', DEFAULT_IBM_PASSWORD)
            self.ibm_event_id = config_dict.get(
                'ibm_event_id', DEFAULT_IBM_EVENT_ID)
            self.ibm_device_type = config_dict.get(
                'ibm_device_type', DEFAULT_IBM_DEVICE_TYPE)
            self.ibm_topic = config_dict.get(
                'ibm_topic', DEFAULT_IBM_TOPIC)
            self.ibm_client_id = config_dict.get(
                'ibm_client_id', DEFAULT_IBM_CLIENT_ID)



            if not self.device_uid:
                self.device_uid = get_mac_address_as_string()

        if not config_file_exists:
            self.save()

    @property
    def as_dictionary(self) -> dict:
        """
        Returns configuration as dict.
        :return: Configuration.
        """
        logging.debug("ESPConfig.as_dictionary()")
        config_dict = {}

        config_dict['cloud_provider'] = self.cloud_provider

        config_dict['access_points'] = self.access_points

        # Connection
        config_dict['data_publishing_period_ms'] = self.data_publishing_period_in_ms
        config_dict['wifi_connection_timeout'] = self.wifi_timeout
        config_dict['mqtt_port'] = self.mqtt_port
        config_dict['mqtt_request_id'] = self.mqqt_request_id
        config_dict['mqtt_port_ssl'] = self.mqtt_port_ssl
        config_dict['mqtt_timeout'] = self.mqtt_timeout
        config_dict['QOS'] = self.QOS
        config_dict['tested_connection_cloud'] = self.tested_connection_cloud
        config_dict['wifi_connection_failed'] = self.wifi_connection_failed

        config_dict['private_key'] = self.private_key
        config_dict['cert_pem'] = self.cert_pem
        config_dict['cert_ca'] = self.cert_ca

        # Sensors
        config_dict['sensor_measurement_pin'] = self.sensor_measurement_pin
        config_dict['sensor_power_pin'] = self.sensor_power_pin
        config_dict['sensor_type'] = self.sensor_type
        config_dict['sensor_sda_pin'] = self.sensor_sda_pin
        config_dict['sensor_scl_pin'] = self.sensor_scl_pin

        # Other
        config_dict['AP_config_done'] = self.ap_config_done
        config_dict['configuration_after_first_power_on_done'] = self.configuration_after_first_power_on_done

        # AWS
        config_dict['aws_endpoint'] = self.aws_endpoint
        config_dict['client_id'] = self.aws_client_id
        config_dict['topic'] = self.aws_topic
        config_dict['device_uid'] = self.device_uid

        # KAA
        config_dict['kaa_user'] = self.kaa_user
        config_dict['kaa_password'] = self.kaa_password
        config_dict['kaa_endpoint'] = self.kaa_endpoint
        config_dict['kaa_app_version'] = self.kaa_app_version
        config_dict['kaa_topic'] = self.kaa_topic

        # ThingsBoard
        config_dict['thingsboard_host'] = self.thingsboard_host
        config_dict['thingsboard_device_client_id'] = self.thingsboard_device_client_id
        config_dict['thingsboard_device_username'] = self.thingsboard_device_username
        config_dict['thingsboard_device_password'] = self.thingsboard_device_password
        config_dict['thingsboard_device_name'] = self.thingsboard_device_name
        config_dict['thingsboard_username'] = self.thingsboard_username
        config_dict['thingsboard_password'] = self.thingsboard_password
        config_dict['thingsboard_jwt_token'] = self.thingsboard_jwt_token
        config_dict['thingsboard_device_id'] = self.thingsboard_device_id
        config_dict['thingsboard_attributes_exists'] = self.thingsboard_attributes_exists

        # Blynk
        config_dict['blynk_auth_token'] = self.blynk_auth_token
        config_dict['blynk_temperature_pin'] = self.blynk_temperature_pin
        config_dict['blynk_humidity_pin'] = self.blynk_humidity_pin

        # IBM
        config_dict['ibm_host'] = self.ibm_host
        config_dict['ibm_device_id'] = self.ibm_device_id
        config_dict['ibm_user'] = self.ibm_user
        config_dict['ibm_organization_id'] = self.ibm_organization_id
        config_dict['ibm_password'] = self.ibm_password
        config_dict['ibm_event_id'] = self.ibm_event_id
        config_dict['ibm_device_type']= self.ibm_device_type
        config_dict['ibm_topic']=self.ibm_topic
        config_dict['ibm_client_id'] = self.ibm_client_id

        return config_dict

    @staticmethod
    def save() -> None:
        """
        Save config to file.
        :return: None.
        """
        logging.debug("ESPConfig.save()")
        global cfg
        config_dict = cfg.as_dictionary

        with open(CONFIG_FILE_PATH, "w", encoding="utf8") as infile:
            dump(config_dict, infile)
        logging.info("New config saved!")

    @staticmethod
    def get_header_with_authorization(jwt_token: str) -> dict:
        standard_header = DEFAULT_JSON_HEADER
        authorization_header = standard_header.copy()
        authorization_header['Authorization'] = "Bearer " + jwt_token
        return authorization_header
