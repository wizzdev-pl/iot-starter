import os
import ujson
import urequests
import logging

from common import config


def authorization_request() -> str:
    logging.debug("Authorization request function")
    headers = config.DEFAULT_JSON_HEADER
    url = config.cfg.api_url + config.API_AUTHORIZATION_URL
    body = {}
    body['is_removed'] = True
    body['created_at'] = 0
    body['username'] = config.cfg.api_login
    body['password'] = config.cfg.api_password

    body = ujson.dumps(body)
    try:
        response = urequests.post(url, data=body, headers=headers)
    except IndexError as e:
        logging.ingo("No internet connection")
        return None
    except Exception as e:
        logging.info("Failed to authorize in API {}".format(e))
        return None

    if response.status_code != '200': #and response.status_code != 200:
        logging.error(response.text)
        return None

    response_dict = response.json()
    jwt_token = response_dict.get("data")
    return jwt_token


def configuration_request(_jwt_token: str):
    headers = get_header_with_authorization(_jwt_token)
    url = config.cfg.api_url + config.API_CONFIG_URL
    thing_name = config.THING_NAME_PREFIX + config.cfg.device_uid
    body = {}
    body['is_removed'] = True
    body['created_at'] = 0
    body['device_id'] = thing_name
    #TODO what values should be below?
    body['description'] = 'Full configuration test'
    body['device_type'] = 'configuration_test'
    body['device_group'] = 'configuration_test'
    body['settings'] = {}

    body = ujson.dumps(body)
    response = urequests.post(url, data=body, headers=headers)
    response_dict = response.json()
    if response_dict is None:
        raise Exception("ESP32 not receive certificates from AWS")
    config.cfg.aws_client_id = thing_name
    config.cfg.save_to_file()
    return get_aws_certs(response_dict)


def get_header_with_authorization(jwt_token: str) -> dict:
    standard_header = config.DEFAULT_JSON_HEADER
    authorization_header = standard_header.copy()
    authorization_header['Authorization'] = "Bearer " + jwt_token
    return authorization_header


def get_aws_certs(_response_dict: dict) -> dict:
    cert_dict = _response_dict.get('data')
    #TODO change keys names in config and erase these three lines
    cert_dict['priv_key'] = cert_dict.pop('PrivateKey')
    cert_dict['cert_pem'] = cert_dict.pop('certificatePem')
    cert_dict['cert_ca'] = cert_dict.pop('certificateCa')
    return cert_dict
