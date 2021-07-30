import ujson
import urequests
from uos import mkdir
from ujson import dump, load
from lib import logging

from communication.wirerless_connection_controller import get_mac_address_as_string
from common import utils


cfg = None

DEFAULT_SSID = 'ssid'
DEFAULT_PASSWORD = 'password'
DEFAULT_AWS_ENDPOINT = 'topic/data'
DEFAULT_AWS_CLIENT_ID = 'default_id'
DEFAULT_AWS_TOPIC = 'topic/data'
DEFAULT_DATA_PUBLISHING_PERIOD_MS = 120000
DEFAULT_USE_DHT = False # DHT - True, BME280 - False
DEFAULT_USE_AWS = True
DEFAULT_DHT_MEASUREMENT_PIN = 4
DEFAULT_SENSOR_POWER_PIN = 26
DEFAULT_DHT_TYPE = "DHT22"
DEFAULT_BME280_SDA_PIN = 21
DEFAULT_BME280_SCL_PIN = 22
DEFAULT_WIFI_TIMEOUT = 5000
DEFAULT_MQTT_PORT = 1883
DEFAULT_MQTT_PORT_SSL = 8883
DEFAULT_MQTT_TIMEOUT = 400
DEFAULT_AP_CONFIG_DONE = False
DEFAULT_NTP_SYNCHRONIZED = False
DEFAULT_CONFIGURATION_AFTER_FIRST_POWER_ON_DONE = False
DEFAULT_DEVICE_UID = ''
DEFAULT_QOS = 1
DEFAULT_API_URL = ""
DEFAULT_API_LOGIN = ""
DEFAULT_API_PASSWORD = ""
CONFIG_FILE_PATH = 'config.json'
DEFAULT_JSON_HEADER = {'Content-Type': 'application/json'}
API_AUTHORIZATION_URL = 'Auth/login'
API_CONFIG_URL = "Device/"
CERTIFICATES_DIR = "/certificates"
KEY_PATH = "{}/{}".format(CERTIFICATES_DIR, "AWS.private_key")
CERTIFICATE_PATH = "{}/{}".format(CERTIFICATES_DIR, "AWS.certificate")
CA_CERTIFICATE_PATH = "{}/{}".format(CERTIFICATES_DIR, "AWS.ca_certificate")
AWS_CONFIG_PATH = "/resources/aws_config.json"
THING_NAME_PREFIX = "ESP32"

DEFAULT_PRIV_KEY = ""
DEFAULT_CERT_PEM = ""
DEFAULT_CERT_CA = ""


DEFAULT_TESTED_CONNECTION_CLOUD = False
DEFAULT_PRINTED_TIME = False
DEFAULT_GOT_SENSOR_DATA = False
DEFAULT_PUBLISHED_TO_CLOUD = False


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
        self.ssid = DEFAULT_SSID
        self.password = DEFAULT_PASSWORD
        self.aws_endpoint = DEFAULT_AWS_ENDPOINT
        self.aws_client_id = DEFAULT_AWS_CLIENT_ID
        self.aws_topic = DEFAULT_AWS_TOPIC
        self.data_publishing_period_in_ms = DEFAULT_DATA_PUBLISHING_PERIOD_MS
        self.use_dht = DEFAULT_USE_DHT
        self.use_aws = DEFAULT_USE_AWS
        self.dht_measurement_pin = DEFAULT_DHT_MEASUREMENT_PIN
        self.sensor_power_pin = DEFAULT_SENSOR_POWER_PIN
        self.dht_type = DEFAULT_DHT_TYPE
        self.bme280_sda_pin = DEFAULT_BME280_SDA_PIN
        self.bme280_scl_pin = DEFAULT_BME280_SCL_PIN
        self.wifi_timeout = DEFAULT_WIFI_TIMEOUT
        self.mqtt_port = DEFAULT_MQTT_PORT
        self.mqtt_port_ssl = DEFAULT_MQTT_PORT_SSL
        self.mqtt_timeout = DEFAULT_MQTT_TIMEOUT
        self.ap_config_done = DEFAULT_AP_CONFIG_DONE
        self.ntp_synchronized = DEFAULT_NTP_SYNCHRONIZED
        self.configuration_after_first_power_on_done = DEFAULT_CONFIGURATION_AFTER_FIRST_POWER_ON_DONE
        self.QOS = DEFAULT_QOS
        self.api_url = DEFAULT_API_URL
        self.api_login = DEFAULT_API_LOGIN
        self.api_password = DEFAULT_API_PASSWORD
        self.device_uid = ""

        self.tested_connection_cloud = DEFAULT_TESTED_CONNECTION_CLOUD
        self.printed_time = DEFAULT_PRINTED_TIME
        self.got_sensor_data = DEFAULT_GOT_SENSOR_DATA
        self.published_to_cloud = DEFAULT_PUBLISHED_TO_CLOUD
        self.private_key = DEFAULT_PRIV_KEY
        self.cert_pem = DEFAULT_CERT_PEM
        self.cert_ca = DEFAULT_CERT_CA

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
            self.ssid = config_dict.get('ssid', DEFAULT_SSID)
            self.password = config_dict.get('password', DEFAULT_PASSWORD)
            self.aws_endpoint = config_dict.get('aws_endpoint', DEFAULT_AWS_ENDPOINT)
            self.aws_client_id = config_dict.get('client_id', DEFAULT_AWS_CLIENT_ID)
            self.aws_topic = config_dict.get('topic', DEFAULT_AWS_TOPIC)
            self.use_aws = config_dict.get('use_aws', DEFAULT_USE_AWS)
            self.data_publishing_period_in_ms = config_dict.get('data_publishing_period_ms',
                                                                DEFAULT_DATA_PUBLISHING_PERIOD_MS)
            self.use_dht = config_dict.get('use_dht', DEFAULT_USE_DHT)
            self.dht_measurement_pin = config_dict.get('dht_measurement_pin', DEFAULT_DHT_MEASUREMENT_PIN)
            self.sensor_power_pin = config_dict.get('sensor_power_pin', DEFAULT_SENSOR_POWER_PIN)
            self.dht_type = config_dict.get('dht_type', DEFAULT_DHT_TYPE)
            self.bme280_sda_pin = config_dict.get('bme280_sda_pin', DEFAULT_BME280_SDA_PIN)
            self.bme280_scl_pin = config_dict.get('bme280_scl_pin', DEFAULT_BME280_SCL_PIN)
            self.wifi_timeout = config_dict.get('wifi_connection_timeout', DEFAULT_WIFI_TIMEOUT)
            self.mqtt_port = config_dict.get('mqtt_port', DEFAULT_MQTT_PORT)
            self.mqtt_port_ssl = config_dict.get('mqtt_port_ssl', DEFAULT_MQTT_PORT_SSL)
            self.mqtt_timeout = config_dict.get('mqtt_timeout', DEFAULT_MQTT_TIMEOUT)
            self.ap_config_done = config_dict.get('AP_config_done', DEFAULT_AP_CONFIG_DONE)
            self.configuration_after_first_power_on_done = \
                config_dict.get('configuration_after_first_power_on_done',
                                DEFAULT_CONFIGURATION_AFTER_FIRST_POWER_ON_DONE)
            self.QOS = config_dict.get('QOS', DEFAULT_QOS)

            self.tested_connection_cloud = config_dict.get('tested_connection_cloud', DEFAULT_TESTED_CONNECTION_CLOUD)
            self.printed_time = config_dict.get('printed_time', DEFAULT_PRINTED_TIME)
            self.got_sensor_data = config_dict.get('got_sensor_data', DEFAULT_GOT_SENSOR_DATA)
            self.published_to_cloud = config_dict.get('published_to_cloud', DEFAULT_PUBLISHED_TO_CLOUD)
            self.private_key = config_dict.get('private_key', DEFAULT_PRIV_KEY)
            self.cert_pem = config_dict.get('cert_pem', DEFAULT_CERT_PEM)
            self.cert_ca = config_dict.get('cert_ca', DEFAULT_CERT_CA)

            if not self.device_uid:
                self.device_uid = config_dict.get('device_uid', DEFAULT_DEVICE_UID)
        if not config_file_exists:
            self.save()

    @staticmethod
    def load_aws_config_from_file() -> dict:
        """
        Load configuration of cloud from file.
        :return: Configuration of cloud in dict.
        """
        with open(AWS_CONFIG_PATH, "r", encoding="utf8") as infile:
            config_dict = load(infile)
        return config_dict

    @property
    def as_dictionary(self) -> dict:
        """
        Returns configuration as dict.
        :return: Configuration.
        """
        logging.debug("ESPConfig.as_dictionary()")
        config_dict = {}
        config_dict['ssid'] = self.ssid
        config_dict['password'] = self.password
        config_dict['aws_endpoint'] = self.aws_endpoint
        config_dict['client_id'] = self.aws_client_id
        config_dict['topic'] = self.aws_topic
        config_dict['use_aws'] = self.use_aws
        config_dict['data_publishing_period_ms'] = self.data_publishing_period_in_ms
        config_dict['use_dht'] = self.use_dht
        config_dict['dht_measurement_pin'] = self.dht_measurement_pin
        config_dict['sensor_power_pin'] = self.sensor_power_pin
        config_dict['dht_type'] = self.dht_type
        config_dict['bme280_sda_pin'] = self.bme280_sda_pin
        config_dict['bme280_scl_pin'] = self.bme280_scl_pin
        config_dict['wifi_connection_timeout'] = self.wifi_timeout
        config_dict['mqtt_port'] = self.mqtt_port
        config_dict['mqtt_port_ssl'] = self.mqtt_port_ssl
        config_dict['mqtt_timeout'] = self.mqtt_timeout
        config_dict['AP_config_done'] = self.ap_config_done
        config_dict['configuration_after_first_power_on_done'] = self.configuration_after_first_power_on_done
        config_dict['device_uid'] = self.device_uid
        config_dict['QOS'] = self.QOS
        config_dict['tested_connection_cloud'] = self.tested_connection_cloud
        config_dict['printed_time'] = self.printed_time
        config_dict['got_sensor_data'] = self.got_sensor_data
        config_dict['published_to_cloud'] = self.published_to_cloud

        config_dict['private_key'] = self.private_key
        config_dict['cert_pem'] = self.cert_pem
        config_dict['cert_ca'] = self.cert_ca

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
    def save_certificates(config_dict: dict) -> None:
        """
        Save AWS certificates to files.
        :param config_dict: dict with credentials.
        :return: None
        """
        global cfg
        logging.debug("save_certificates()")
        try:
            mkdir(CERTIFICATES_DIR)
        except:
            pass

        if 'cert_pem' in config_dict.keys():
            certificate_string = config_dict['cert_pem']
            cfg.cert_pem = config_dict['cert_pem']
            with open(CERTIFICATE_PATH, "w", encoding="utf8") as infile:
                infile.write(certificate_string)

        if 'priv_key' in config_dict.keys():
            private_key_string = config_dict['priv_key']
            cfg.private_key = config_dict['priv_key']
            logging.info(private_key_string)
            with open(KEY_PATH, "w", encoding="utf8") as infile:
                infile.write(private_key_string)

        if 'cert_ca' in config_dict.keys():
            ca_certificate_string = config_dict['cert_ca']
            cfg.cert_ca = config_dict['cert_ca']
            with open(CA_CERTIFICATE_PATH, "w", encoding="utf8") as infile:
                infile.write(ca_certificate_string)

    @staticmethod
    def read_certificates(parse: bool = False) -> (bool, str, str):
        """
        Read certificates from files.
        :return: Error code (True - OK, False - at least one certificate does not exist), text of certificates.
        """
        logging.debug("read_certificates()")
        result, aws_certificate = utils.read_from_file(CERTIFICATE_PATH)
        result2, aws_key = utils.read_from_file(KEY_PATH)

        if parse:
            aws_certificate.replace('\n', '')
            aws_key.replace('\n', '')
            return (result and result2), aws_certificate, aws_key
        else:
            return (result and result2), aws_certificate, aws_key

    @staticmethod
    def update_config_dict(new_config: dict) -> None:
        """
        Updates configuration.
        :param new_config: New configuration.
        :return: None
        """
        logging.debug("update_config_dict()")
        file_path = 'config.json'
        with open(file_path, "r", encoding="utf8") as infile:
            old_config = load(infile)
        modified_entries = 0
        for key in old_config.keys():
            try:
                if old_config[key] != new_config[key]:
                    logging.debug('Changing config entry: {} \n from: {}, to: {}'.format(key,
                                                                                         old_config[key],
                                                                                         new_config[key]))
                    old_config[key] = new_config[key]
                    modified_entries += 1
            except:
                pass

        if modified_entries > 0:
            with open(file_path, "w", encoding="utf8") as infile:
                dump(old_config, infile)
            logging.debug('Modified {} entrires. Config updated succesfully!'.format(modified_entries))
        else:
            logging.debug('No changes to config file were made!')

    @staticmethod
    def authorization_request() -> str:
        """
        Register your ESP in cloud. It takes password and login from aws_config.json
        :return: JSON Web Token
        """
        global cfg
        logging.debug("Authorization request function")
        headers = DEFAULT_JSON_HEADER
        url = cfg.api_url + API_AUTHORIZATION_URL
        body = {}
        body['is_removed'] = True
        body['created_at'] = 0
        body['username'] = cfg.api_login
        body['password'] = cfg.api_password

        logging.debug('LOGIN: {}, password: {}'.format(cfg.api_login, cfg.api_password))

        body = ujson.dumps(body)
        try:
            response = urequests.post(url, data=body, headers=headers)
        except IndexError as e:
            logging.info("No internet connection: {}".format(e))
            return ""
        except Exception as e:
            logging.info("Failed to authorize in API {}".format(e))
            return ""

        if response.status_code != '200' and response.status_code != 200:
            logging.error(response.text)
            return ""

        response_dict = response.json()
        jwt_token = response_dict.get("data")
        return jwt_token

    @staticmethod
    def configuration_request(_jwt_token: str):
        """
        Function configures ESP with cloud (AWS)
        :param _jwt_token: JSON Web Token
        :return: dict with certificates/keys
        """
        global cfg
        headers = ESPConfig.get_header_with_authorization(_jwt_token)
        url = cfg.api_url + API_CONFIG_URL
        thing_name = THING_NAME_PREFIX + cfg.device_uid
        body = {}
        body['is_removed'] = True
        body['created_at'] = 0
        body['device_id'] = thing_name
        body['description'] = 'Full configuration test'
        body['device_type'] = 'configuration_test'
        body['device_group'] = 'configuration_test'
        body['settings'] = {}

        body = ujson.dumps(body)
        response = urequests.post(url, data=body, headers=headers)
        response_dict = response.json()
        if response_dict is None:
            raise Exception("ESP32 not receive certificates from AWS")
        cfg.aws_client_id = thing_name
        cfg.save()
        return ESPConfig.get_aws_certs(response_dict)

    @staticmethod
    def get_header_with_authorization(jwt_token: str) -> dict:
        standard_header = DEFAULT_JSON_HEADER
        authorization_header = standard_header.copy()
        authorization_header['Authorization'] = "Bearer " + jwt_token
        return authorization_header

    @staticmethod
    def get_aws_certs(_response_dict: dict) -> dict:
        cert_dict = _response_dict.get('data')
        cert_dict['priv_key'] = cert_dict.pop('PrivateKey')
        cert_dict['cert_pem'] = cert_dict.pop('certificatePem')
        cert_dict['cert_ca'] = cert_dict.pop('certificateCa')
        return cert_dict
