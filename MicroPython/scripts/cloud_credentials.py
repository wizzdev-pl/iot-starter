import argparse
import logging
import json
from pathlib import Path


KAA_CONFIG_SRC_PATH = 'src/kaa_config.json'


def file_exists(path):
    if Path(path).is_file():
        return True
    else:
        return False


def set_credentials():
    """
    Asks user for credentials for Kaa cloud similar to "awscli"
    """
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

    endpoint = input("Device endpoint [{}]: ".format(old_endpoint))
    app_version = input("App version [{}]: ".format(old_app_version))
    user = input("User [{}]: ".format(old_user))
    password = input("Password [{}]: ".format(old_password))
    print()

    # If values were not updated; leave the old ones
    config['kaa_endpoint'] = endpoint if endpoint else old_endpoint
    config['kaa_app_version'] = app_version if app_version else old_app_version
    config['kaa_user'] = user if user else old_user
    config['kaa_password'] = password if password else old_password

    with open(KAA_CONFIG_SRC_PATH, 'w', encoding='utf8') as outfile:
        json.dump(config, outfile)


def parse_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--set-credentials', required=True, action='store_true',
        dest='creds', help="Set credentials needed for cloud service"
    )

    args = vars(parser.parse_args())
    return args


if __name__ == '__main__':
    args = parse_arguments()

    if args['creds']:
        set_credentials()
    else:
        logging.info('Please run the script with "--set-credentials" flag!')

