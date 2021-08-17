import ssl
from json import dumps, loads

from paho.mqtt.client import Client

RESULT_CODES = {
    1: "incorrect protocol version",
    2: "invalid client identifier",
    3: "server unavailable",
    4: "bad username or password",
    5: "not authorised",
}


class ProvisionClient(Client):
    PROVISION_REQUEST_TOPIC = "/provision/request"
    PROVISION_RESPONSE_TOPIC = "/provision/response"

    def __init__(self, host, port, provision_request, client_public):
        super().__init__()
        self._host = host
        self._port = port
        self._username = "provision"
        self._cert = client_public
        self.tls_set(ca_certs="certs/mqttserver.pub.pem",
                     tls_version=ssl.PROTOCOL_TLSv1_2)
        self.on_connect = self.__on_connect
        self.on_message = self.__on_message
        self.__provision_request = provision_request

    def __on_connect(self, client, userdata, flags, rc):  # Callback for connect
        if rc == 0:
            print("[Provisioning client] Connected to ThingsBoard ")
            # Subscribe to provisioning response topic
            client.subscribe(self.PROVISION_RESPONSE_TOPIC)
            provision_request = dumps(self.__provision_request)
            print("[Provisioning client] Sending provisioning request {}".format(
                provision_request))
            # Publishing provisioning request topic
            client.publish(self.PROVISION_REQUEST_TOPIC, provision_request)
        else:
            print("[Provisioning client] Cannot connect to ThingsBoard!, result: {}".format(
                RESULT_CODES[rc]))

    def __on_message(self, client, userdata, msg):
        decoded_payload = msg.payload.decode("UTF-8")
        print("[Provisioning client] Received data from ThingsBoard: {}".format(
            decoded_payload))
        decoded_message = loads(decoded_payload)
        provision_device_status = decoded_message.get("status")
        if provision_device_status == "SUCCESS":
            if decoded_message["credentialsValue"] == self._cert.replace("-----BEGIN CERTIFICATE-----\n", "") \
                                                          .replace("-----END CERTIFICATE-----\n", "") \
                                                          .replace("\n", ""):
                print(
                    "[Provisioning client] Provisioning success! Certificates are saved.")
            else:
                print(
                    "[Provisioning client] Returned certificate is not equal to sent one.")
        else:
            print("[Provisioning client] Provisioning was unsuccessful with status {} and message: {}".format(
                provision_device_status, decoded_message["errorMsg"]))
        self.disconnect()

    def provision(self):
        print("[Provisioning client] Connecting to ThingsBoard (provisioning client)")
        self.__clean_credentials()
        self.connect(self._host, self._port, 60)
        self.loop_forever()

    @staticmethod
    def __clean_credentials():
        open("certs/credentials", "w").close()
