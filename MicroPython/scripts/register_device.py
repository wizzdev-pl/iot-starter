import argparse
import json
from common.utilities import file_exists
from cloud_credentials import THINGSBOARD_CONFIG_SRC_PATH
import sys
from json import loads

from communication.provision_client import ProvisionClient, RESULT_CODES


def collect_data():
    if file_exists(THINGSBOARD_CONFIG_SRC_PATH):
        with open(THINGSBOARD_CONFIG_SRC_PATH, 'r', encoding='utf8') as infile:
            config = json.load(infile)
    else:
        config = {}

    credentials = ProvisionClient.get_credentials()
    if credentials is not None:
        credentials = loads(credentials)
    else:
        credentials = {}

    config = {
        'thingsboard_host': config.get('thingsboard_host', 'localhost'),
        'port': config.get('port', 1883),
        'thingsboard_client_id': credentials.get('clientId', None),
        'thingsboard_user': credentials.get('userName', None),
        'thingsboard_password': credentials.get('password', None)
    }

    host = input("\nPlease write your ThingsBoard \033[93mhost\033[0m or leave it blank to use default [{}]: ".format(
        config['thingsboard_host']))
    if host:
        config["thingsboard_host"] = host

    port = input("Please write your ThingsBoard \033[93mMQTT port\033[0m or leave it blank to use default [{}]: ".format(
        config['port']))
    if port:
        config["port"] = int(port)

    config["provision_device_key"] = input("Please write \033[93mprovision device key\033[0m: ")
    config["provision_device_secret"] = input("Please write \033[93mprovision device secret\033[0m: ")

    clientID = input("Please write your ThingsBoard \033[93mclient ID\033[0m [{}]: ".format(
        config['thingsboard_client_id']))
    user = input("Please write your ThingsBoard \033[93musername\033[0m [{}]: ".format(
        config['thingsboard_user']))
    password = input("Please write your ThingsBoard \033[93mpassword\033[0m [{}]: ".format(
        config['thingsboard_password']))

    if clientID:
        config['thingsboard_client_id'] = clientID
    if user:
        config['thingsboard_user'] = user
    if password:
        config['thingsboard_password'] = password

    device_name = input("Please write \033[93mdevice name\033[0m or leave it blank to generate: ")
    if device_name:
        config["thingsboard_device_name"] = device_name

    return config


def on_connected(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to ThingsBoard with credentials: username: {}, password: {}, client id: {}".format(
            client._username.decode(), client._password.decode(), client._client_id.decode()))
    else:
        print("Cannot connect to ThingsBoard!, result: {}".format(
            RESULT_CODES[rc]))


def save_config(config):
    with open(THINGSBOARD_CONFIG_SRC_PATH, 'w', encoding='utf8') as cfg_file:
        json.dump(config, cfg_file)


def parse_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument('-c', '--cloud', metavar='CLOUD', type=str, required=True,
                        help="Cloud provider for IoT Starter")

    args = vars(parser.parse_args())
    return args


if __name__ == '__main__':
    args = parse_arguments()

    if args['cloud'] != 'THINGSBOARD':
        print('Script for registering new devices works only for THINGSBOARD currently!')
        sys.exit(-1)

    config = collect_data()

    provision_request = {
        "provisionDeviceKey": config["provision_device_key"],
        "provisionDeviceSecret": config["provision_device_secret"],
        "credentialsType": "MQTT_BASIC",
        "clientId": config["thingsboard_client_id"],
        "username": config["thingsboard_user"],
        "password": config["thingsboard_password"]
    }

    if config.get('thingsboard_device_name', None) is not None:
        provision_request['deviceName'] = config['thingsboard_device_name']

    provision_client = ProvisionClient(
        config['thingsboard_host'], config['port'], provision_request)
    provision_client.provision()

    client = provision_client.get_new_client()
    if client:
        client.on_connect = on_connected
        client.connect(config['thingsboard_host'], config['port'])
        save_config(config)
    else:
        print("Device was not created!")
        sys.exit(-1)
