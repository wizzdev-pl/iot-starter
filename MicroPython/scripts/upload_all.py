import argparse
import time
import os

from upload_scripts import flash_scripts
from upload_micropython import flash_micropython, erase_chip
from generate_terraform import save_terraform_output_as_file

TERRAFORM_OUTPUT_PATH = "src/aws_config.json"


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', metavar='PORT', type=str, required=True,
                        help="Com port of the device")

    args = vars(parser.parse_args())
    return args


if __name__ == '__main__':
    args = parse_arguments()

    if not os.path.isfile(TERRAFORM_OUTPUT_PATH):
        print("Generating terraform output..")
        save_terraform_output_as_file(TERRAFORM_OUTPUT_PATH)
    erase_chip(args['port'])
    flash_micropython(args['port'])
    time.sleep(4)
    flash_scripts(args['port'], TERRAFORM_OUTPUT_PATH)
