import argparse
import sys
from pathlib import Path
from subprocess import call, Popen, PIPE

from communication.provision_client import ProvisionClient
from common.utilities import file_exists

KEYGEN_PROPERTIES = "scripts/keygen.properties"
SERVER_CREDS_SCRIPT = "./scripts/server.keygen.sh"
CLIENT_CREDS_SCRIPT = "./scripts/client.keygen.sh"
CERTS_DIR = "certs/"
SERVER_CER_FILE = "mqttserver.cer"

def generate_server_creds():
    keygen_properties_present()
    rc = call(SERVER_CREDS_SCRIPT)
    if rc != 0:
        print("Aborting! Creating server certificates failed with return code: {}".format(rc))
        sys.exit(-1)


def generate_client_creds():
    keygen_properties_present()
    if not file_exists(CERTS_DIR + SERVER_CER_FILE):
        print("No server certficiates found in {} directory! Make sure to run {} first!".format(
            CERTS_DIR, SERVER_CREDS_SCRIPT))
        print("Aborting!")
        sys.exit(-1)

    rc = call(CLIENT_CREDS_SCRIPT)
    if rc != 0:
        print("Aborting! Creating server certificates failed with return code: {}".format(rc))
        sys.exit(-1)

def keygen_properties_present():
    if not file_exists(KEYGEN_PROPERTIES):
        print("Configuration file for keygen was not found!")
        print("Please make sure that keygen.properties file " +
              "exists in the same directory as keygen scripts")
        print("Aborting!")
        sys.exit(-1)


def change_owner():
    whoami = "whoami"
    user, error = Popen(whoami, stdout=PIPE).communicate()

    chown = ["sudo", "chown", "-R", user.decode().strip(), CERTS_DIR]
    output, error = Popen(chown, stdout=PIPE).communicate()
    if error is not None:
        print("Error in chown command for certificates: {}".format(error))
        sys.exit(-1)


def generate_credentials():
    if not file_exists(CERTS_DIR + "mqttserver.cer"):
        generate_server_creds()
    generate_client_creds()
    change_owner()


def collect_data():
    config = {
        'host': 'localhost',
        'port': 8883,
        'client_public': CERTS_DIR + "mqttclient.pub.pem"
    }
    host = input("\nPlease write your ThingsBoard \033[93mhost\033[0m or leave it blank to use default (localhost): ")
    if host:
        config["host"] = host

    port = input("Please write your ThingsBoard \033[93mSSL port\033[0m or leave it blank to use default (8883): ")
    if port:
        config["port"] = int(port)

    config["provision_device_key"] = input("Please write \033[93mprovision device key\033[0m: ")
    config["provision_device_secret"] = input("Please write \033[93mprovision device secret\033[0m: ")

    client_public = input("Please write \033[93mfile name\033[0m if your \033[93mclient public certificate\033[0m or leave it blank to use default (mqttclient.pub.pem): ")
    if client_public:
        config['client_public'] = CERTS_DIR + client_public

    fname, _ = Path(config['client_public']).stem.split('.')
    device_name = input("Please write \033[93mdevice name\033[0m or leave it blank to use default ({}): ".format(
        fname))
    if device_name:
        config["device_name"] = device_name
    else:
        config["device_name"] = fname

    return config

def read_client_pub_pem(client_public):
    cert = None
    try:
        with open(client_public, "r") as cert_file:
            cert = cert_file.read()
    except Exception as e:
        print("Cannot read certificate with error: {}".format(e))

    return cert

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

    generate_credentials()

    config = collect_data()
    cert = read_client_pub_pem(config['client_public'])

    if cert is not None:
        provision_request = {
            "provisionDeviceKey": config["provision_device_key"],
            "provisionDeviceSecret": config["provision_device_secret"],
            "deviceName": config["device_name"],
            "hash": cert,
            "credentialsType": "X509_CERTIFICATE"
        }

        provision_client = ProvisionClient(
            config['host'], config['port'], provision_request, cert)
        provision_client.provision()
    else:
        print("Cannot read client public certificate!")
        sys.exit(-1)
