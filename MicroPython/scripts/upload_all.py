import argparse
import json
import time
import os

from cloud_credentials import set_credentials
from upload_scripts import flash_scripts
from upload_micropython import flash_micropython, erase_chip
from generate_terraform import save_terraform_output_as_file

TERRAFORM_OUTPUT_PATH = "src/aws_config.json"
KAA_CONFIG_PATH = 'src/kaa_config.json'
CONFIG_OUTPUT_PATH = "src/config.json"


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', metavar='PORT', type=str, required=True,
                        help="Com port of the device")
    parser.add_argument('-c', '--cloud', metavar='CLOUD', type=str, required=True,
                        help="Cloud provider for IoT Starter")

    args = vars(parser.parse_args())
    return args


def save_cloud_provider(cloud_provider):
    """
    Save cloud provider to use on device.
    This script cannot access config file so it needs to create config file in advance
    """
    cfg = {'cloud_provider': cloud_provider}
    with open(CONFIG_OUTPUT_PATH, 'w') as outfile:
        json.dump(cfg, outfile)


if __name__ == '__main__':
    args = parse_arguments()

    if args['cloud'] == 'AWS':
        if not os.path.isfile(TERRAFORM_OUTPUT_PATH):
            print("Generating terraform output..")
            save_terraform_output_as_file(TERRAFORM_OUTPUT_PATH)
        cloud_config_file_path = TERRAFORM_OUTPUT_PATH
    elif args['cloud'] == 'KAA':
        cloud_config_file_path = KAA_CONFIG_PATH
        set_credentials()
    else:
        # Hardcoded cloud providers, as we cannot access config file (CPyton vs MicroPython)
        # TODO: How to avoid hardcoded values like these???
        raise Exception("Wrong cloud provider! Only: AWS, KAA are valid")
    
    save_cloud_provider(args['cloud'])
    erase_chip(args['port'])
    flash_micropython(args['port'])
    time.sleep(4)
    flash_scripts(args['port'], cloud_config_file_path)
