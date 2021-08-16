import argparse
import logging
import json
from pathlib import Path


KAA_CONFIG_SRC_PATH = 'src/kaa_config.json'
THINGSBOARD_CONFIG_SRC_PATH = 'src/thingsboard_config.json'

def file_exists(path):
    if Path(path).is_file():
        return True
    else:
        return False


def set_credentials(cloud):
    """
    Asks user for credentials for cloud similar to "awscli"
    """
    if cloud == "KAA":
        if file_exists(KAA_CONFIG_SRC_PATH):
            with open(KAA_CONFIG_SRC_PATH, 'r', encoding='utf8') as infile:
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
        config['kaa_endpoint'] = endpoint if endpoint else old_endpoint
        config['kaa_app_version'] = app_version if app_version else old_app_version
        config['kaa_user'] = user if user else old_user
        config['kaa_password'] = password if password else old_password

        with open(KAA_CONFIG_SRC_PATH, 'w', encoding='utf8') as outfile:
            json.dump(config, outfile)

    elif cloud == "THINGSBOARD":
        if file_exists(THINGSBOARD_CONFIG_SRC_PATH):
            with open(THINGSBOARD_CONFIG_SRC_PATH, 'r', encoding='utf8') as infile:
                config = json.load(infile)
        else:
            config = {}
        
        print("Please provide ThingsBoard credentials:")
        old_host = config.get('thingsboard_host', None)
        old_server_public = config.get('server_public', None)
        old_client_public = config.get('client_public', None)

        host = input("Hostname [{}]: ".format(old_host))
        server_public = input("Public server certificate path [{}]: ".format(old_server_public))
        client_public = input("Public client certificate path [{}]: ".format(old_client_public))

        # If values were not updated; leave the old ones
        config['thingsboard_host'] = host if host else old_host
        config['server_public'] = server_public if server_public else old_server_public
        config['client_public'] = client_public if client_public else old_client_public

        with open(THINGSBOARD_CONFIG_SRC_PATH, 'w', encoding='utf8') as outfile:
            json.dump(config, outfile)


def parse_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument('-c', '--cloud', metavar='CLOUD', type=str, required=True,
                        help="Cloud provider for IoT Starter")

    args = vars(parser.parse_args())
    return args


if __name__ == '__main__':
    args = parse_arguments()

    if args['cloud'] not in ('AWS', 'KAA', 'THINGSBOARD'):
        print('Invalid choice! Only: AWS / KAA / THINGSBOARD clouds are supported!')
    else:
        set_credentials(args['cloud'])

