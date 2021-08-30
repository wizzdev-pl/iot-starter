from json import dumps, loads

from common.utilities import file_exists, remove_file
from paho.mqtt.client import Client

RESULT_CODES = {
    1: "incorrect protocol version",
    2: "invalid client identifier",
    3: "server unavailable",
    4: "bad username or password",
    5: "not authorised",
}

CREDENTIALS_PATH = 'src/credentials.txt'


class ProvisionClient(Client):
    PROVISION_REQUEST_TOPIC = "/provision/request"
    PROVISION_RESPONSE_TOPIC = "/provision/response"

    def __init__(self, host, port, provision_request):
        super().__init__()
        self._host = host
        self._port = port
        self._username = "provision"
        self.on_connect = self.__on_connect
        self.on_message = self.__on_message
        self.__provision_request = provision_request

    def __on_connect(self, client, userdata, flags, rc):  # Callback for connect
        if rc == 0:
            print("Provisioning device to ThingsBoard")
            client.subscribe(self.PROVISION_RESPONSE_TOPIC)
            provision_request = dumps(self.__provision_request)
            client.publish(self.PROVISION_REQUEST_TOPIC, provision_request)
        else:
            print("Cannot connect to ThingsBoard!, result: {}".format(
                RESULT_CODES[rc]))

    def __on_message(self, client, userdata, msg):
        decoded_payload = msg.payload.decode("UTF-8")
        decoded_message = loads(decoded_payload)
        provision_device_status = decoded_message.get("status")
        if provision_device_status == "SUCCESS":
            self.__save_credentials(decoded_message["credentialsValue"])
            print("Provisioning successful! New device registered.")
        else:
            print("Provisioning was unsuccessful with status {} and message: {}".format(
                provision_device_status, decoded_message["errorMsg"]))
            # Needed as it can cause errors while checking if device was created
            remove_file(CREDENTIALS_PATH, suppress=True)

        self.disconnect()

    def provision(self):
        self.__clean_credentials()
        self.connect(self._host, self._port, 60)
        self.loop_forever()

    def get_new_client(self):
        client_credentials = self.get_credentials()
        if client_credentials is None:
            client_credentials = {}
        else:
            client_credentials = loads(client_credentials)

        new_client = None
        if client_credentials:
            new_client = Client(client_id=client_credentials["clientId"])
            new_client.username_pw_set(
                client_credentials["userName"], client_credentials["password"])
        else:
            print("Cannot read credentials from file!")
        return new_client

    @staticmethod
    def get_credentials():
        new_credentials = None
        if file_exists(CREDENTIALS_PATH):
            with open(CREDENTIALS_PATH, "r") as credentials_file:
                new_credentials = credentials_file.read()
        return new_credentials

    @staticmethod
    def __save_credentials(credentials):
        with open(CREDENTIALS_PATH, "w") as credentials_file:
            credentials_file.write(dumps(credentials))

    @staticmethod
    def __clean_credentials():
        if file_exists(CREDENTIALS_PATH):
            open(CREDENTIALS_PATH, "w").close()
