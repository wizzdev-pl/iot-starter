import argparse
import json
import os
import time

from cloud_credentials import set_credentials
from common.cloud_providers import Providers
from generate_terraform import save_terraform_output_as_file
from upload_micropython import erase_chip, flash_micropython
from upload_scripts import flash_scripts

CLOUD_CONFIG_PATH = "src/{}_config.json"
CONFIG_OUTPUT_PATH = "config.json"


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', metavar='PORT', type=str, required=True,
                        help="Com port of the device")
    parser.add_argument('-c', '--cloud', metavar='CLOUD', type=str, required=True,
                        help="Cloud provider for IoT Starter: {}".format(
                            Providers.print_providers()))
    parser.add_argument('-s', '--sensor', metavar='SENSOR', type=str, required=False,
                        help="Sensor type in use (defaults to DHT22)")

    args = vars(parser.parse_args())
    return args


def save_additional_arguments(cloud_provider, sensor_type):
    """
    Save additional arguments (cloud provider and sensor in use)
    This script cannot access config file so it needs to create config file in advance
    """
    if sensor_type == None:
        sensor_type = "DHT22"

    cfg = {'cloud_provider': cloud_provider, 'sensor_type': sensor_type}
    with open("src/" + CONFIG_OUTPUT_PATH, 'w') as outfile:
        json.dump(cfg, outfile)


if __name__ == '__main__':
    args = parse_arguments()

    cloud_config_file_path = CLOUD_CONFIG_PATH.format(args['cloud'].lower())
    if args['cloud'] == Providers.AWS:
        if not os.path.isfile(cloud_config_file_path):
            print("Generating terraform output..")
            save_terraform_output_as_file(cloud_config_file_path)
    elif args['cloud'] in (Providers.KAA, Providers.THINGSBOARD, Providers.BLYNK, Providers.IBM):
        set_credentials(args['cloud'])
    else:
        raise Exception("Wrong cloud provider! Only: {} are valid".format(
            Providers.print_providers()))

    save_additional_arguments(args['cloud'], args['sensor'])
    erase_chip(args['port'])
    flash_micropython(args['port'])
    time.sleep(4)
    flash_scripts(args['port'], cloud_config_file_path, args['cloud'], CONFIG_OUTPUT_PATH)
