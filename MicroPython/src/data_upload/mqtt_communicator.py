import uos
import utime
import logging
import ujson

from umqtt.simple import MQTTClient  # micropython-umqtt library

from common import config
from common import utils

import gc


class MQTTCommunicator:
    def __init__(self,
                 use_AWS,
                 client_id,
                 endpoint,
                 port,
                 timeout,
                 ):
        self.is_connected = False
        self.use_AWS = use_AWS
        self.client_id = client_id
        self.endpoint = endpoint
        self.port = port
        self.device_shadow_get_topic = '$aws/things/{}/shadow/get'.format(client_id)
        self.device_shadow_accepted_topic = '$aws/things/{}/shadow/get/accepted'.format(client_id)
        self.device_shadow_update_topic = '$aws/things/{}/shadow/update'.format(client_id)
        self.timeout = timeout
        if use_AWS:
            result, AWS_certificate, AWS_key = config.read_certificates()
            AWS_certificate.replace('\n', '')
            AWS_key.replace('\n', '')
            if not result:
                raise Exception ("Failed to read AWS certificate or key")
            ssl_parameters = {
                "server_side": False,
                "key": AWS_key,
                "cert": AWS_certificate
            }
            self.MQTT_client = MQTTClient(client_id=self.client_id,
                                          server=self.endpoint,
                                          port=self.port,
                                          ssl=True,
                                          keepalive=self.timeout,
                                          ssl_params=ssl_parameters)

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
        try:
            gc.collect()
            result = self.MQTT_client.connect(clean_session=False)
            self.is_connected = result
            if result:
                return True, ""
            else:
                return False, "Failed to connect to MQTT server"
        except Exception as e:
            self.is_connected = False
            return False, "Exception during connection to MQTT server. Exception occurred {}".format(e)
        except NotImplementedError as e:
            self.is_connected = False
            return False, "Exception during connection to MQTT server. Not implemented error occured {}".format(e)

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
        Substribes to given topic
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

    def get_device_shadow(self, timeout_ms: int) -> bool:
        """
        Getting information about device.
        :param timeout_ms: timeout.
        :return: Error code (True - OK, False - Error).
        """
        self.subscribe(topic=self.device_shadow_accepted_topic, callback=self._get_device_shadow_callback, qos=0)
        self.publish(topic=self.device_shadow_get_topic, data='', qos=0)  # Empty msg triggers AWS response to /update

        if self._wait_for_message(timeout_ms):
            message = "Could not update device shadow, timed out! [{}]".format(timeout_ms)
            try:
                with open("errorlog.txt", "a") as file:
                    file.write(message)
            except:
                logging.error(message)
                logging.error("Can't write to errorlog.txt")
            return False
        return True

    @staticmethod
    def _get_device_shadow_callback(topic, msg):
        shadow = ujson.loads(msg)
        try:
            new_config = shadow['state']['desired']['config']
        except:
            logging.info("There was no config in the 'desired' segment.")
            return

        config.update_config_dict(new_config)

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

    def update_device_shadow_startup(self, power_on_timestamp):
        logging.debug("MQTTCommunicator({})".format(power_on_timestamp))
        updated_config = {'state': {}}
        updated_config['state']['reported'] = {}
        updated_config['state']['reported']['config'] = config.cfg.as_dictionary
        updated_config['state']['reported']['power_on_timestamp'] = power_on_timestamp
        #updated_config['state']['reported']['last_commit_info'] = utils.get_last_commit_info()
        logging.info('Updating shadow device info and config')
        data = ujson.dumps(updated_config)
        logging.debug("data to send = {}".format(data))
        self.publish(data, '$aws/things/{}/shadow/update'.format(self.client_id), 0)
        utime.sleep(0.25)

