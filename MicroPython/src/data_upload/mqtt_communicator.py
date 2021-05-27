from cloud.AWS_cloud import AWS_cloud
from cloud.KAA_cloud import KAA_cloud
import utime
import logging
import ujson

from umqtt.simple import MQTTClient  # micropython-umqtt library

from common import config
from common import utils

import gc


class MQTTCommunicator:
    def __init__(self,
                 cloud_provider,
                 client_id,
                 endpoint,
                 port,
                 timeout,
                 ):
        self.is_connected = False
        self.cloud_provider = cloud_provider
        self.client_id = client_id
        self.endpoint = endpoint
        self.port = port
        self.timeout = timeout

        # TODO: Create MQTTClient based on cloud provider from config.cfg (maybe method for switch case?)
        if cloud_provider == 'AWS':
            result, aws_certificate, aws_key = AWS_cloud.read_certificates(True)
            if not result:
                raise Exception("Failed to read AWS certificate or key")
            ssl_parameters = {
                "server_side": False,
                "key": aws_key,
                "cert": aws_certificate
            }
            self.MQTT_client = MQTTClient(client_id=self.client_id,
                                          server=self.endpoint,
                                          port=self.port,
                                          ssl=True,
                                          keepalive=self.timeout,
                                          ssl_params=ssl_parameters)
        
        # TODO: Implement MQTT for other clients like KAA
        else:
            self.MQTT_client = MQTTClient(client_id=self.client_id,
                                          server=self.endpoint,
                                          port=self.port)

    def __del__(self):
        if self.is_connected:
            self.disconnect()

    def connect(self) -> (bool, str):
        """
        Connect to MQTT Server.
        :return: Error code (True - OK, False - Error).
        """
        logging.debug("mqtt_communicator.py/connect()")
        try:
            gc.collect()
            result = self.MQTT_client.connect(clean_session=False)
            self.is_connected = result
            if result:
                return True, ""
            else:
                raise Exception("Failed to connect to MQTT server")
        except ValueError as e:
            self.is_connected = False
            raise ValueError(e)
        except Exception as e:
            self.is_connected = False
            raise Exception(e)
        except NotImplementedError as e:
            self.is_connected = False
            raise Exception(e)

    def disconnect(self) -> None:
        """
        Disconnect from MQTT Server.
        :return: None
        """
        if self.is_connected:
            self.MQTT_client.disconnect()
            self.is_connected = False

    def publish(self, data, topic, qos) -> bool:
        """
        :param data: data to be published
        :param topic: name of the topic to be published to default /topic/data
        :param qos: level of QOS to use either 0 or 1
        :return: Error code (True - OK, False - Error).
        :example: publish('19.7', '/office/room_3/temperature', 0)
        """
        if not self.is_connected:
            logging.info("Publish called but not connected to MQTT broker!")
            return False

        gc.collect()
        try:
            self.MQTT_client.publish(topic=topic, msg=data, qos=qos)
            logging.info("Publishing with MQTT at %s:%d" % (self.MQTT_client.server, self.MQTT_client.port))
        except Exception as e:
            try:
                self.disconnect()
                logging.error("Failed to publish MQTT message at %s:%d. Exception occured %s" %
                              (self.MQTT_client.server, self.MQTT_client.port, e))
            except:
                pass  # probably not connected
        return True

    def subscribe(self, topic, callback, qos) -> bool:
        """
        Subscribes to given topic
        :param topic: topic to subscribe to.
        :param callback: callback function.
        :param qos: Quality of Service.
        :return: Error code (True - OK, False - Error).
        """
        if not self.is_connected:
            logging.info("Subscribe called but not connected to MQTT broker!")
            return False

        self.MQTT_client.set_callback(callback)
        self.MQTT_client.subscribe(topic=topic, qos=qos)
        logging.info("Subscribing to {} with MQTT at {}:{}".format(topic, self.endpoint, self.port))
        return True

    def _wait_for_message(self, timeout_ms: int = None):
        wait_time = 0
        if timeout_ms is None:
            timeout_ms = 1000
        while wait_time < timeout_ms:
            self.MQTT_client.check_msg()
            utime.sleep(0.1)
            wait_time += 100
        return False

    def publish_message(self, payload, topic, qos):
        mqtt_message = {
            'client_id': self.client_id,
            'publish_timestamp': utils.get_current_timestamp_ms(),
            'data': payload
        }
        gc.collect()  # run garbage collector to clean up memory
        try:
            if self.publish(data=ujson.dumps(mqtt_message), topic=topic, qos=qos):  # if qos == 1 it's a blocking method
                logging.debug("Publishing mesage succesfull")
                return True
            else:
                logging.debug("Problem with publishing mesage")
                return False
        except MemoryError as e:
            try:
                with open("errorlog.txt", "a") as file:
                    file.write(str(e))
            except:
                logging.error(str(e))
                logging.error("Can't write to errorlog.txt")
            return False
