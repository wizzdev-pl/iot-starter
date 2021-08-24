import gc
import logging
import urequests
import machine
from ujson import dumps, load
from os import mkdir

from common import config, utils
from communication import wirerless_connection_controller
from cloud.cloud_interface import CloudProvider


class AWS_cloud(CloudProvider):
    def device_configuration(self, data: list[dict]) -> int:
        """
        Configures device in the cloud. Function used as hook to web_app.
        :param data: parameters to connect to wifi.
        :return: Error code (0 - OK, 1 - Error).
        """
        logging.info("Wifi access point configuration:")

        for access_point in data:
            logging.info("Ssid: {} Password: {}".format(access_point["ssid"], access_point["password"]))

        wireless_controller = wirerless_connection_controller.get_wireless_connection_controller_instance()
        try:
            utils.connect_to_wifi(wireless_controller, data)
            logging.info(wireless_controller.sta_handler.ifconfig())
            self.configure_aws_thing()
            config.cfg.access_points = data
        except Exception as e:
            logging.error("Exception caught: {}".format(e))
            config.cfg.access_points = config.DEFAULT_ACCESS_POINTS
            config.cfg.save()
            return -1

        config.cfg.ap_config_done = True
        config.cfg.save()
        machine.reset()

        return 0

    def configure_aws_thing(self) -> bool:
        """
        Register ESP as thing in AWS cloud.
        :return: Error code (True - OK, False - Error).
        """
        logging.debug("AWS_cloud/confirue_aws_thing()")
        logging.info(
            "Allocated bytes on heap before gc {}".format(gc.mem_alloc()))
        gc.collect()
        logging.info(
            "Allocated bytes on heap after gc {}".format(gc.mem_alloc()))
        self.configure_data_from_terraform()
        logging.debug("Authorization request...")
        jwt_token = self.authorization_request()
        if jwt_token is not "":
            cert_dict = self.configuration_request(jwt_token)
            self.save_certificates(cert_dict)
            logging.debug("Configuration done")
            return True
        else:
            logging.error("Problem with authorization")
            event = MainControllerEvent(MainControllerEventType.ERROR_OCCURRED)
            self.add_event(event)
            return False

    def configure_data_from_terraform(self) -> None:
        """
        Setup data from terraform to connect to AWS.
        :return: None
        """
        logging.debug("AWS_cloud/configure_data_from_terraform()")
        aws_configuration = self.load_aws_config_from_file()
        if 'aws_iot_endpoint' in aws_configuration.keys():
            config.cfg.aws_endpoint = aws_configuration['aws_iot_endpoint'].get(
                "value").get("endpoint_address")

        if 'visualization_url' in aws_configuration.keys():
            visualization_url = aws_configuration['visualization_url'].get(
                "value")
            config.cfg.api_url = 'https://' + visualization_url + '/api/'

        if 'esp_login' in aws_configuration.keys():
            config.cfg.api_login = aws_configuration['esp_login'].get("value")

        if 'esp_password' in aws_configuration.keys():
            config.cfg.api_password = aws_configuration['esp_password'].get(
                "value")

        config.cfg.save()

        logging.debug("Configure data from terraform ends")

    @staticmethod
    def save_certificates(config_dict: dict) -> None:
        """
        Save AWS certificates to files.
        :param config_dict: dict with credentials.
        :return: None
        """
        logging.debug("save_certificates()")
        try:
            mkdir(config.CERTIFICATES_DIR)
        except:
            pass

        if 'cert_pem' in config_dict.keys():
            certificate_string = config_dict['cert_pem']
            config.cfg.cert_pem = config_dict['cert_pem']
            with open(config.CERTIFICATE_PATH, "w", encoding="utf8") as infile:
                infile.write(certificate_string)

        if 'priv_key' in config_dict.keys():
            private_key_string = config_dict['priv_key']
            config.cfg.private_key = config_dict['priv_key']
            logging.info(private_key_string)
            with open(config.KEY_PATH, "w", encoding="utf8") as infile:
                infile.write(private_key_string)

        if 'cert_ca' in config_dict.keys():
            ca_certificate_string = config_dict['cert_ca']
            config.cfg.cert_ca = config_dict['cert_ca']
            with open(config.CA_CERTIFICATE_PATH, "w", encoding="utf8") as infile:
                infile.write(ca_certificate_string)

    @staticmethod
    def read_certificates(parse: bool = False) -> tuple(bool, str, str):
        """
        Read certificates from files.
        :return: Error code (True - OK, False - at least one certificate does not exist), text of certificates.
        """
        logging.debug("AWS_cloud/read_certificates()")
        result, aws_certificate = utils.read_from_file(config.CERTIFICATE_PATH)
        result2, aws_key = utils.read_from_file(config.KEY_PATH)

        if parse:
            aws_certificate.replace('\n', '')
            aws_key.replace('\n', '')
            return (result and result2), aws_certificate, aws_key
        else:
            return (result and result2), aws_certificate, aws_key

    def get_aws_certs(self, _response_dict: dict) -> dict:
        cert_dict = _response_dict.get('data')
        cert_dict['priv_key'] = cert_dict.pop('PrivateKey')
        cert_dict['cert_pem'] = cert_dict.pop('certificatePem')
        cert_dict['cert_ca'] = cert_dict.pop('certificateCa')
        return cert_dict

    def authorization_request(self) -> str:
        """
        Register your ESP in cloud. It takes password and login from aws_config.json
        :return: JSON Web Token
        """
        logging.debug("Authorization request function")
        headers = config.DEFAULT_JSON_HEADER
        url = config.cfg.api_url + config.AWS_API_AUTHORIZATION_URL
        body = {
            'is_removed': True,
            'created_at': 0,
            'username': config.cfg.api_login,
            'password': config.cfg.api_password
        }

        logging.debug('LOGIN: {}, password: {}'.format(
            config.cfg.api_login, config.cfg.api_password))

        body = dumps(body)
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

    def configuration_request(self, _jwt_token: str) -> dict:
        """
        Function configures ESP with cloud (AWS)
        :param _jwt_token: JSON Web Token
        :return: dict with certificates/keys
        """
        headers = config.ESPConfig.get_header_with_authorization(_jwt_token)
        url = config.cfg.api_url + config.AWS_API_CONFIG_URL
        thing_name = config.AWS_THING_NAME_PREFIX + config.cfg.device_uid
        body = {
            'is_removed': True,
            'created_at': 0,
            'device_id': thing_name,
            'description': 'Full configuration test',
            'device_type': 'configuration_test',
            'device_group': 'configuration_test',
            'settings': {}
        }

        body = dumps(body)
        response = urequests.post(url, data=body, headers=headers)
        response_dict = response.json()
        if response_dict is None:
            raise Exception("ESP32 not receive certificates from AWS")
        config.cfg.aws_client_id = thing_name
        config.cfg.save()
        return self.get_aws_certs(response_dict)

    def load_aws_config_from_file(self) -> dict:
        """
        Load configuration of AWS from file.
        :return: Configuration in dict.
        """
        with open(config.AWS_CONFIG_PATH, "r", encoding="utf8") as infile:
            config_dict = load(infile)
        return config_dict

    def publish_data(self, data) -> None:
        wireless_controller, mqtt_communicator = utils.get_wifi_and_cloud_handlers(
            sync_time=False
        )

        certificates_existence, *_ = self.read_certificates()
        if not certificates_existence:
            logging.debug("No AWS Certificates, configure_aws_thing()")
            self.configure_aws_thing()

        logging.debug("data to send = {}".format(data))
        logging.info(config.cfg.aws_topic)
        result = mqtt_communicator.publish_message(payload=data, topic=config.cfg.aws_topic,
                                                   qos=config.cfg.QOS)

        if not result:
            logging.error("Error publishing data to MQTT in publish_data()")

        mqtt_communicator.disconnect()
        wireless_controller.disconnect_station()
