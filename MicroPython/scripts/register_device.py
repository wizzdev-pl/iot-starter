import argparse
import json
import sys
from json import loads

from cloud_credentials import CLOUD_CONFIG_PATH
from common.cloud_providers import Providers
from common.utilities import file_exists
from communication.provision_client import RESULT_CODES, ProvisionClient


def collect_data():
    if file_exists(CLOUD_CONFIG_PATH):
        with open(CLOUD_CONFIG_PATH, 'r', encoding='utf8') as infile:
            config = json.load(infile)
    else:
        config = {}

    credentials = ProvisionClient.get_credentials()
    if credentials is not None and credentials != "":
        credentials = loads(credentials)
    else:
        print("Credentials not found, using default!")
        credentials = {}

    host = input("\nPlease write your ThingsBoard host or leave it blank to use default [{}]: ".format(
        config.get('thingsboard_host', 'localhost')))
    if host:
        config["thingsboard_host"] = host
    elif config.get('thingsboard_host', None) is None:
        config["thingsboard_host"] = 'localhost'

    provision_device_key = input("Please write provision device key [{}]: ".format(
        config.get('provision_device_key', None)))
    provision_device_secret = input("Please write provision device secret [{}]: ".format(
        config.get('provision_device_secret', None)))

    if provision_device_key:
        config['provision_device_key'] = provision_device_key
    if provision_device_secret:
        config['provision_device_secret'] = provision_device_secret

    clientID = input("Please write ThingsBoard client ID for your device [{}]: ".format(
        credentials.get('clientId', None)))
    device_username = input("Please write ThingsBoard username for your device [{}]: ".format(
        credentials.get('userName', None)))
    device_password = input("Please write ThingsBoard password for your device [{}]: ".format(
        credentials.get('password', None)))

    if clientID:
        config['thingsboard_device_client_id'] = clientID
    if device_username:
        config['thingsboard_device_username'] = device_username
    if device_password:
        config['thingsboard_device_password'] = device_password

    device_name = input("Please write your device name or leave blank to use previous one [{}]: ".format(
        config.get('thingsboard_device_name', None)))

    if device_name:
        config["thingsboard_device_name"] = device_name
    elif config['thingsboard_device_name'] is None:
        print("Device name must be supplied! Please restart the script.")
        sys.exit(-1)

    return config


def on_connected(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to ThingsBoard with credentials: username: {}, password: {}, client id: {}".format(
            client._username.decode(), client._password.decode(), client._client_id.decode()))
    else:
        print("Cannot connect to ThingsBoard!, result: {}".format(
            RESULT_CODES[rc]))


def save_config(config):
    with open(CLOUD_CONFIG_PATH, 'w', encoding='utf8') as cfg_file:
        json.dump(config, cfg_file)


def parse_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument('-c', '--cloud', metavar='CLOUD', type=str, required=True,
                        help="Cloud provider for IoT Starter: {}".format(
                            Providers.THINGSBOARD))

    args = vars(parser.parse_args())
    return args


if __name__ == '__main__':
    args = parse_arguments()

    if args['cloud'] != Providers.THINGSBOARD:
        print('Script for registering new devices works only for THINGSBOARD currently!')
        sys.exit(-1)

    config = collect_data()

    provision_request = {
        "provisionDeviceKey": config["provision_device_key"],
        "provisionDeviceSecret": config["provision_device_secret"],
        "credentialsType": "MQTT_BASIC",
        "clientId": config["thingsboard_device_client_id"],
        "username": config["thingsboard_device_username"],
        "password": config["thingsboard_device_password"]
    }

    if config.get('thingsboard_device_name', None) is not None:
        provision_request['deviceName'] = config['thingsboard_device_name']

    if not None in provision_request.values():
        provision_client = ProvisionClient(
            config['thingsboard_host'], port=1883, provision_request=provision_request)
        provision_client.provision()
    else:
        print("At least one provided credential is empty! Aborting...")
        sys.exit(-1)

    client = provision_client.get_new_client()
    if client:
        client.on_connect = on_connected
        client.connect(config['thingsboard_host'], port=1883)
        save_config(config)
    else:
        print("Device was not created!")
        sys.exit(-1)
