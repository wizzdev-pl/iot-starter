import argparse
from subprocess import call
import sys

CLIENT_CREDS_SCRIPT = "./scripts/test.sh"


def generate_client_creds():
    rc = call(CLIENT_CREDS_SCRIPT)
    if rc != 0:
        print("Aborting! Script failed with return code: {}".format(rc))
        sys.exit()


def parse_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument('-c', '--cloud', metavar='CLOUD', type=str, required=True,
                        help="Cloud provider for IoT Starter")

    args = vars(parser.parse_args())
    return args


if __name__ == '__main__':
    args = parse_arguments()

    if args['cloud'] not in ('THINGSBOARD'):
        print('Script for registering new devices works only for THINGSBOARD currently!')
    else:
        generate_client_creds()