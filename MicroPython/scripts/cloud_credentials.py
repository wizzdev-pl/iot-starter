import argparse
import json

from common.cloud_providers import Providers
from common.utilities import file_exists

CLOUD_CONFIG_PATH = "src/{}_config.json"


def set_credentials(cloud):
    """
    Asks user for credentials for cloud similar to "awscli"
    """
    cloud_config_path = CLOUD_CONFIG_PATH.format(cloud.lower())
    if cloud == Providers.KAA:
        if file_exists(cloud_config_path):
            with open(cloud_config_path, 'r', encoding='utf8') as infile:
                config = json.load(infile)
        else:
            config = {}
        print("Please provide kaa credentials:")
        old_endpoint = config.get('kaa_endpoint', None)
        old_app_version = config.get('kaa_app_version', None)
        old_user = config.get('kaa_user', None)
        old_password = config.get('kaa_password', None)

        endpoint = input("Device endpoint token [{}]: ".format(old_endpoint))
        app_version = input("App version [{}]: ".format(old_app_version))
        user = input("User [{}]: ".format(old_user))
        password = input("Password [{}]: ".format(old_password))

        # If values were not updated; leave the old ones
        if endpoint:
            config['kaa_endpoint'] = endpoint
        if app_version:
            config['kaa_app_version'] = app_version
        if user:
            config['kaa_user'] = user
        if password:
            config['kaa_password'] = password

        with open(cloud_config_path, 'w', encoding='utf8') as outfile:
            json.dump(config, outfile)

    elif cloud == Providers.THINGSBOARD:
        if file_exists(cloud_config_path):
            with open(cloud_config_path, 'r', encoding='utf8') as infile:
                config = json.load(infile)
        else:
            config = {}

        print("Please provide ThingsBoard credentials:")
        old_host = config.get('thingsboard_host', None)
        old_client_id = config.get('thingsboard_device_client_id', None)
        old_device_username = config.get('thingsboard_device_username', None)
        old_device_password = config.get('thingsboard_device_password', None)
        old_device_name = config.get('thingsboard_device_name', None)
        old_username = config.get('thingsboard_username', None)
        old_password = config.get('thingsboard_password', None)

        host = input("Hostname [{}]: ".format(old_host))
        client_id = input("Client ID [{}]: ".format(old_client_id))
        device_username = input(
            "Device username [{}]: ".format(old_device_username))
        device_password = input(
            "Device password [{}]: ".format(old_device_password))
        device_name = input("Device name [{}]: ".format(old_device_name))
        username = input("ThingsBoard username [{}]: ".format(old_username))
        password = input("ThingsBoard password [{}]: ".format(old_password))

        # If values were not updated; leave the old ones
        if host:
            config['thingsboard_host'] = host
        if client_id:
            config['thingsboard_device_client_id'] = client_id
        if device_username:
            config['thingsboard_device_username'] = device_username
        if device_password:
            config['thingsboard_device_password'] = device_password
        if device_name:
            config['thingsboard_device_name'] = device_name
        if username:
            config['thingsboard_username'] = username
        if password:
            config['thingsboard_password'] = password

        with open(cloud_config_path, 'w', encoding='utf8') as outfile:
            json.dump(config, outfile)

    elif cloud == Providers.BLYNK:
        if file_exists(cloud_config_path):
            with open(cloud_config_path, 'r', encoding='utf8') as infile:
                config = json.load(infile)
        else:
            config = {}

        print("Please provide Blynk credentials:")
        old_auth_token = config.get('blynk_auth_token', None)
        old_temp_pin = config.get('blynk_temp_pin', None)
        old_humidity_pin = config.get('blynk_humidity_pin', None)

        auth_token = input("Authentication token [{}]: ".format(old_auth_token))
        temp_pin = input("Temperature virtual pin [{}]: ".format(old_temp_pin))
        humidity_pin = input("Humidity virtual pin [{}]: ".format(old_humidity_pin))

        # If values were not updated; leave the old ones
        if auth_token:
            config['blynk_auth_token'] = auth_token
        if temp_pin:
            config['blynk_temp_pin'] = temp_pin
        if humidity_pin:
            config['blynk_humidity_pin'] = humidity_pin

        with open(cloud_config_path, 'w', encoding='utf8') as outfile:
            json.dump(config, outfile)


def parse_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument('-c', '--cloud', metavar='CLOUD', type=str, required=True,
                        help="Cloud provider for IoT Starter: {}".format(
                            Providers.print_providers()))

    args = vars(parser.parse_args())
    return args


if __name__ == '__main__':
    args = parse_arguments()

    if args['cloud'] not in Providers.get_providers():
        print('Invalid choice! Only:',
              Providers.print_providers(), 'clouds are supported!')
    else:
        set_credentials(args['cloud'])
