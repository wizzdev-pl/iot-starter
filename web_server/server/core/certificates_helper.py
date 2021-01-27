import config

import requests
import os


class CertificatesHandler:

    def __init__(self, client):
        self.client = client
        self.__certificates = {}
        self.cert_arn = None

    def get_certificates(self):
        cert_response = self.client.create_keys_and_certificate(setAsActive=True)
        self.__certificates['PrivateKey'] = cert_response['keyPair']['PrivateKey']
        self.__certificates['certificatePem'] = cert_response['certificatePem']

        # Save cert_arn for the future
        self.cert_arn = cert_response['certificateArn']

        self.get_ca_cert()
        return self.__certificates

    def get_ca_cert(self):
        ca_cert_response = requests.get(config.AWS_ROOT_CA_CERTIFICATE_URL)
        self.__certificates['certificateCa'] = ca_cert_response.content.decode("utf-8")



