import gc
import logging
from os import mkdir
from typing import Tuple

import machine
import urequests
from common import config, utils
from common.config import cfg
from communication import wirerless_connection_controller
from controller.main_controller_event import (MainControllerEvent,
                                              MainControllerEventType)
from ujson import dumps, load

from cloud.cloud_interface import CloudProvider


class AWS_cloud(CloudProvider):
    def __init__(self) -> None:
        pass

    def device_configuration(self, data: dict) -> int:
        """
        Configures device in the cloud. Function used as hook to web_app.
        :param data: parameters to connect to wifi.
        :return: Error code (0 - OK, 1 - Error).
        """
        ssid = data['ssid']
        password = data['password']

        cfg.ssid = ssid
        cfg.password = password
        cfg.save()

        logging.info(
            "Wifi config. Wifi ssid {} Wifi password {}".format(ssid, password))

        wireless_controller = wirerless_connection_controller.get_wireless_connection_controller_instance()
        try:
            utils.connect_to_wifi(wireless_controller)
            logging.info(wireless_controller.sta_handler.ifconfig())
            self.configure_aws_thing()
        except Exception as e:
            logging.error("Exception catched: {}".format(e))
            event = MainControllerEvent(MainControllerEventType.ERROR_OCCURRED)
            self.add_event(event)
            return 1

        cfg.ap_config_done = True
        cfg.save()
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
            cfg.aws_endpoint = aws_configuration['aws_iot_endpoint'].get(
                "value").get("endpoint_address")

        if 'visualization_url' in aws_configuration.keys():
            visualization_url = aws_configuration['visualization_url'].get(
                "value")
            cfg.api_url = 'https://' + visualization_url + '/api/'

        if 'esp_login' in aws_configuration.keys():
            cfg.api_login = aws_configuration['esp_login'].get("value")

        if 'esp_password' in aws_configuration.keys():
            cfg.api_password = aws_configuration['esp_password'].get(
                "value")

        cfg.save()

        logging.debug("Configure data from terraform ends")

    def save_certificates(self, config_dict: dict) -> None:
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
            cfg.cert_pem = config_dict['cert_pem']
            with open(config.CERTIFICATE_PATH, "w", encoding="utf8") as infile:
                infile.write(certificate_string)

        if 'priv_key' in config_dict.keys():
            private_key_string = config_dict['priv_key']
            cfg.private_key = config_dict['priv_key']
            logging.info(private_key_string)
            with open(config.KEY_PATH, "w", encoding="utf8") as infile:
                infile.write(private_key_string)

        if 'cert_ca' in config_dict.keys():
            ca_certificate_string = config_dict['cert_ca']
            cfg.cert_ca = config_dict['cert_ca']
            with open(config.CA_CERTIFICATE_PATH, "w", encoding="utf8") as infile:
                infile.write(ca_certificate_string)

    def read_certificates(self, parse: bool = False) -> Tuple(bool, str, str):
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
        url = cfg.api_url + config.API_AUTHORIZATION_URL
        body = {}
        body['is_removed'] = True
        body['created_at'] = 0
        body['username'] = cfg.api_login
        body['password'] = cfg.api_password

        logging.debug('LOGIN: {}, password: {}'.format(
            cfg.api_login, cfg.api_password))

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
        url = cfg.api_url + config.API_CONFIG_URL
        thing_name = config.THING_NAME_PREFIX + cfg.device_uid
        body = {}
        body['is_removed'] = True
        body['created_at'] = 0
        body['device_id'] = thing_name
        body['description'] = 'Full configuration test'
        body['device_type'] = 'configuration_test'
        body['device_group'] = 'configuration_test'
        body['settings'] = {}

        body = dumps(body)
        response = urequests.post(url, data=body, headers=headers)
        response_dict = response.json()
        if response_dict is None:
            raise Exception("ESP32 not receive certificates from AWS")
        cfg.aws_client_id = thing_name
        cfg.save()
        return self.get_aws_certs(response_dict)

    def load_aws_config_from_file(self) -> dict:
        """
        Load configuration of AWS from file.
        :return: Configuration in dict.
        """
        with open(config.AWS_CONFIG_PATH, "r", encoding="utf8") as infile:
            config_dict = load(infile)
        return config_dict

    def publish_data(self) -> None:

        wireless_controller, mqtt_communicator = utils.get_wifi_and_aws_handlers(
            sync_time=False)

        certificates_existence, *_ = self.read_certificates()
        if not certificates_existence:
            logging.debug("No AWS Certificates, configure_aws_thing()")
            self.configure_aws_thing()

        logging.debug("data to send = {}".format(self.data_acquisitor.data))
        logging.info(cfg.aws_topic)
        result = mqtt_communicator.publish_message(payload=self.data_acquisitor.data, topic=cfg.aws_topic,
                                                   qos=cfg.QOS)

        if not result:
            logging.error("Error publishing data to MQTT in send_data()")

        mqtt_communicator.disconnect()
        wireless_controller.disconnect_station()
