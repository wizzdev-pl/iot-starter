from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient
import os
import sys

CLIENT_ID = "ESP32840d8ee67d9c"
HOST = "a1kdus6mbpzad4.iot.eu-west-3.amazonaws.com"
PORT = 8883
ROOT_CA_PATH = "/home/developer/Projects/wizzdev-iot-starter/MicroPython/src/certificates/AWS.ca_certificate"
PRIVATE_KEY_PATH = "/home/developer/Projects/wizzdev-iot-starter/MicroPython/src/certificates/AWS.private_key"
CERTIFICATE_PATH = "/home/developer/Projects/wizzdev-iot-starter/MicroPython/src/certificates/AWS.certificate"


# Init AWSIoTMQTTShadowClient
myAWSIoTMQTTShadowClient = AWSIoTMQTTShadowClient(CLIENT_ID)
myAWSIoTMQTTShadowClient.configureEndpoint(HOST, PORT)
myAWSIoTMQTTShadowClient.configureCredentials(ROOT_CA_PATH,
                                              PRIVATE_KEY_PATH,
                                              CERTIFICATE_PATH)

# AWSIoTMQTTShadowClient connection configuration
myAWSIoTMQTTShadowClient.configureAutoReconnectBackoffTime(1, 32, 20)
myAWSIoTMQTTShadowClient.configureConnectDisconnectTimeout(10) # 10 sec
myAWSIoTMQTTShadowClient.configureMQTTOperationTimeout(25) # 5 sec

# Connect to AWS IoT
myAWSIoTMQTTShadowClient.connect()
print("DONE")