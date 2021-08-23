from cloud.AWS_cloud import AWS_cloud
from cloud.KAA_cloud import KAA_cloud
from cloud.Things_cloud import ThingsBoard
from cloud.cloud_interface import Providers
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
                 timeout,
                 ):
        logging.debug("data_upload/MQTTCommunicator.__init__()")
        self.is_connected = False
        self.cloud_provider = cloud_provider
        self.timeout = timeout

        if cloud_provider == Providers.AWS:
            # Secure socket layer MQTT communication
            
            result, aws_certificate, aws_key = AWS_cloud.read_certificates(True)
            if not result:
                raise Exception("Failed to read AWS certificate or key")
            
            ssl_parameters = {
                "server_side": False,
                "key": aws_key,
                "cert": aws_certificate
            }

            self.server = config.cfg.aws_endpoint
            self.client_id = config.cfg.aws_client_id
            self.port = config.cfg.mqtt_port_ssl

            self.MQTT_client = MQTTClient(
                client_id=self.client_id,
                server=self.server,
                port=self.port,
                ssl=True,
                keepalive=self.timeout,
                ssl_params=ssl_parameters
            )

        elif cloud_provider == Providers.KAA:
            # Default MQTT port
            self.port = config.cfg.mqtt_port
            self.server = config.DEFAULT_KAA_KPC_HOST
            self.client_id = config.cfg.kaa_endpoint

            self.MQTT_client = MQTTClient(
                client_id=self.client_id,
                server=self.server,
                port=self.port,
                keepalive=self.timeout,
                user=config.cfg.kaa_user,
                password=config.cfg.kaa_password
            )

        elif cloud_provider == Providers.THINGSBOARD:
            self.port = config.cfg.mqtt_port
            self.server = config.cfg.thingsboard_host
            self.client_id = config.cfg.thingsboard_client_id
            self.user = config.cfg.thingsboard_user
            self.password = config.cfg.thingsboard_password

            self.MQTT_client = MQTTClient(
                client_id=self.client_id,
                server=self.server,
                port=self.port,
                keepalive=self.timeout,
                user=self.user,
                password=self.password
            )

        else:
            # Not implemented for other clouds yet
            self.MQTT_client = MQTTClient(
                client_id=self.client_id,
                server=self.server,
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
            self.MQTT_client.connect(False)
            self.is_connected = True
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
            logging.info("Publishing with MQTT at %s:%d" %
                         (self.MQTT_client.server, self.MQTT_client.port))
        except Exception as e:
            try:
                self.disconnect()
                logging.error("Failed to publish MQTT message at %s:%d. Exception occured %s" %
                              (self.MQTT_client.server, self.MQTT_client.port, e))
            except:
                pass  # probably not connected
        return True

    def set_callback(self, callback) -> bool:
        """
        Sets callback to MQTT client for all received messages for all topics
        :param callback: Callback function for received message
        :return: Error code (True - OK, False - Error)
        """
        if not self.is_connected:
            logging.info(
                "Setting callback called but not connected to MQTT broker!"
            )
            return False

        self.MQTT_client.set_callback(callback)
        logging.info("Setting callback for all topics with MQTT at {}:{}".format(
            self.server, self.port
        ))

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
        logging.info("Subscribing to {} with MQTT at {}:{}".format(
            topic, self.server, self.port))
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
        
        if config.cfg.cloud_provider == Providers.AWS:
            mqtt_message = {
                'client_id': self.client_id,
                'publish_timestamp': utils.get_current_timestamp_ms(),
                'data': payload
            }
        else:
            mqtt_message = payload
        # Run garbage collector to clean up memory
        gc.collect()
        try:
            # if qos == 1 it's a blocking method
            if self.publish(data=ujson.dumps(mqtt_message), topic=topic, qos=qos):
                if config.cfg.cloud_provider in (Providers.AWS, Providers.THINGSBOARD):
                    logging.info("Publishing mesage succesfull!")
                # Kaa subscribes to specific topics to know if publish is successful or not
                return True
            else:
                logging.error("Problem with publishing mesage!")
                return False
        except MemoryError as e:
            try:
                with open("errorlog.txt", "a") as file:
                    file.write(str(e))
            except:
                logging.error(str(e))
                logging.error("Can't write to errorlog.txt")
            return False
