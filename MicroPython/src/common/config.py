from machine import Pin, reset, SLEEP, DEEPSLEEP
from esp32 import wake_on_ext0, WAKEUP_ALL_LOW, WAKEUP_ANY_HIGH
from lib import logging
from data_upload.handlers_container import HandlerContainer
from communication.wirerless_connection_controller import get_mac_address_as_string
from common import utils
from ujson import dump, load
from uos import mkdir

cfg = None
hc = None

DEFAULT_SSID = 'ssid'
DEFAULT_PASSWORD = 'password'
DEFAULT_LOCAL_ENDPOINT = ''
DEFAULT_AWS_ENDPOINT = 'topic/data'
DEFAULT_AWS_CLIENT_ID = 'default_id'
DEFAULT_AWS_TOPIC = 'topic/data'
DEFAULT_DATA_PUBLISHING_PERIOD_MS = 120000
DEFAULT_USE_DHT = True
DEFAULT_USE_AWS = True
DEFAULT_DHT_MEASUREMENT_PIN = 4
DEFAULT_DHT_POWER_PIN = 26
DEFAULT_DHT_TYPE = "DHT22"
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
        self.local_endpoint = DEFAULT_LOCAL_ENDPOINT
        self.aws_endpoint = DEFAULT_AWS_ENDPOINT
        self.aws_client_id = DEFAULT_AWS_CLIENT_ID
        self.aws_topic = DEFAULT_AWS_TOPIC
        self.data_publishing_period_in_ms = DEFAULT_DATA_PUBLISHING_PERIOD_MS
        self.use_dht = DEFAULT_USE_DHT
        self.use_aws = DEFAULT_USE_AWS
        self.dht_measurement_pin = DEFAULT_DHT_MEASUREMENT_PIN
        self.dht_power_pin = DEFAULT_DHT_POWER_PIN
        self.dht_type = DEFAULT_DHT_TYPE
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
        self.device_uid = ""  # leave empty so you it won't wake up WLAN when working in deep sleep mode

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
                self.device_uid = get_mac_address_as_string()  # set only if config does not exist
                dump(empty_config, file)

        with open(CONFIG_FILE_PATH, "r", encoding="utf8") as infile:
            config_dict = load(infile)
            self.ssid = config_dict.get('ssid', DEFAULT_SSID)
            self.password = config_dict.get('password', DEFAULT_PASSWORD)
            self.local_endpoint = config_dict.get('local_endpoint', DEFAULT_LOCAL_ENDPOINT)
            self.aws_endpoint = config_dict.get('aws_endpoint', DEFAULT_AWS_ENDPOINT)
            self.aws_client_id = config_dict.get('client_id', DEFAULT_AWS_CLIENT_ID)
            self.aws_topic = config_dict.get('topic', DEFAULT_AWS_TOPIC)
            self.use_aws = config_dict.get('use_aws', DEFAULT_USE_AWS)
            self.data_publishing_period_in_ms = config_dict.get('data_publishing_period_ms',
                                                                DEFAULT_DATA_PUBLISHING_PERIOD_MS)
            self.use_dht = config_dict.get('use_dht', DEFAULT_USE_DHT)
            self.dht_measurement_pin = config_dict.get('dht_measurement_pin', DEFAULT_DHT_MEASUREMENT_PIN)
            self.dht_power_pin = config_dict.get('dht_power_pin', DEFAULT_DHT_POWER_PIN)
            self.dht_type = config_dict.get('dht_type', DEFAULT_DHT_TYPE)
            self.wifi_timeout = config_dict.get('wifi_connection_timeout', DEFAULT_WIFI_TIMEOUT)
            self.mqtt_port = config_dict.get('mqtt_port', DEFAULT_MQTT_PORT)
            self.mqtt_port_ssl = config_dict.get('mqtt_port_ssl', DEFAULT_MQTT_PORT_SSL)
            self.mqtt_timeout = config_dict.get('mqtt_timeout', DEFAULT_MQTT_TIMEOUT)
            self.ap_config_done = config_dict.get('AP_config_done', DEFAULT_AP_CONFIG_DONE)
            self.configuration_after_first_power_on_done = \
                config_dict.get('configuration_after_first_power_on_done',
                                DEFAULT_CONFIGURATION_AFTER_FIRST_POWER_ON_DONE)
            self.QOS = config_dict.get('QOS', DEFAULT_QOS)
            if not self.device_uid:
                self.device_uid = config_dict.get('device_uid', DEFAULT_DEVICE_UID)
        if not config_file_exists:
            self.save_to_file()

    def load_aws_config_from_file(self) -> dict:
        """
        Load configuration of cloud from file.
        :return: Configuration of cloud in dict.
        """
        with open(AWS_CONFIG_PATH, "r", encoding="utf8") as infile:
            config_dict = load(infile)
        return config_dict

    def save_to_file(self) -> None:
        """
        Save configuration to file.
        :return: None
        """
        logging.debug("ESPConfig.save_to_file()")
        config_dict = self.as_dictionary

        with open(CONFIG_FILE_PATH, "w", encoding="utf8") as infile:
            dump(config_dict, infile)
        logging.info("New config saved!")

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
        config_dict['local_endpoint'] = self.local_endpoint
        config_dict['aws_endpoint'] = self.aws_endpoint
        config_dict['client_id'] = self.aws_client_id
        config_dict['topic'] = self.aws_topic
        config_dict['use_aws'] = self.use_aws
        config_dict['data_aquisition_period_ms'] = self.data_aqusition_period_in_ms
        config_dict['data_publishing_period_ms'] = self.data_publishing_period_in_ms
        config_dict['use_dht'] = self.use_dht
        config_dict['dht_measurement_pin'] = self.dht_measurement_pin
        config_dict['dht_power_pin'] = self.dht_power_pin
        config_dict['dht_type'] = self.dht_type
        config_dict['wifi_connection_timeout'] = self.wifi_timeout
        config_dict['mqtt_port'] = self.mqtt_port
        config_dict['mqtt_port_ssl'] = self.mqtt_port_ssl
        config_dict['mqtt_timeout'] = self.mqtt_timeout
        config_dict['AP_config_done'] = self.ap_config_done
        config_dict['configuration_after_first_power_on_done'] = self.configuration_after_first_power_on_done
        config_dict['device_uid'] = self.device_uid
        config_dict['QOS'] = self.QOS
        config_dict['blink_led'] = self.blink_led
        config_dict['blue_led_pin'] = self.blue_led_pin

        return config_dict


def button_irq(p: Pin) -> None:
    """
    Callback of interrupt of BOOT button. Resets ESP.
    :param p: BOOT pin.
    :return: None
    """
    logging.debug("=== RESET BUTTON PRESSED ===")
    save()
    reset()


def reset_config(p: Pin) -> None:
    """
    Callback of interrupt of button on GPIO32. Resets configuration of ESP (config.json changes to default one).
    :param p: GPIO32 pin.
    :return: None
    """
    logging.debug("=== CONFIG BUTTON PRESSED ===")
    global cfg
    cfg.ap_config_done = False
    cfg.ssid = DEFAULT_SSID
    cfg.password = DEFAULT_PASSWORD
    save()
    reset()


def init() -> None:
    """
    Initialize ESP, reads or creates configuration, sets interrupts.
    :return: None
    """
    logging.debug("config.py/init()")
    global cfg
    global hc
    hc = HandlerContainer()
    cfg = ESPConfig()
    cfg.load_from_file()

    button = Pin(0, Pin.IN, Pin.PULL_UP)
    button.irq(trigger=Pin.IRQ_FALLING, handler=button_irq)
    wake_on_ext0(pin=button, level=False)

    button2 = Pin(32, Pin.IN, Pin.PULL_UP)
    button2.irq(trigger=Pin.IRQ_FALLING, handler=reset_config)
    wake_on_ext0(pin=button2, level=WAKEUP_ALL_LOW)

    logging.debug("Configuration loaded")


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


def save_certificates(config_dict: dict) -> None:
    """
    Save AWS certificates to files.
    :param config_dict: dict with credentials.
    :return: None
    """
    logging.debug("save_certificates()")
    try:
        mkdir(CERTIFICATES_DIR)
    except:
        # Already exists I can not logging it here
        pass

    if 'cert_pem' in config_dict.keys():
        certificate_string = config_dict['cert_pem']
        with open(CERTIFICATE_PATH, "w", encoding="utf8") as infile:
            infile.write(certificate_string)

    if 'priv_key' in config_dict.keys():
        private_key_string = config_dict['priv_key']
        logging.info(private_key_string)
        with open(KEY_PATH, "w", encoding="utf8") as infile:
            infile.write(private_key_string)

    if 'cert_ca' in config_dict.keys():
        ca_certificate_string = config_dict['cert_ca']
        with open(CA_CERTIFICATE_PATH, "w", encoding="utf8") as infile:
            infile.write(ca_certificate_string)


def read_certificates() -> (bool, str, str):
    """
    Read certificates from files.
    :return: Error code (True - OK, False - at least one certificate does not exist), text of certificates.
    """
    logging.debug("read_certificates()")
    result, AWS_certificate = utils.read_from_file(CERTIFICATE_PATH)
    result2, AWS_key = utils.read_from_file(KEY_PATH)

    return (result and result2), AWS_certificate, AWS_key


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
