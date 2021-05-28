import logging

import ujson
from common import config, utils

from cloud.cloud_interface import CloudProvider


class KAA_cloud(CloudProvider):
    def __init__(self) -> None:
        # TODO: We need those topics but maybe load them from file
        # instead of creating them from config???
        self.publish_success_topic = config.cfg.kaa_success_topic
        self.publish_error_topic = config.cfg.kaa_error_topic

    def receive_message(self, topic, msg) -> None:
        """
        Callback method for MQTT client
        :param topic: Topic of the message received encoded as bytes
        :param msg: Message received encoded as bytes
        :return: None 
        """
        topic = topic.decode()

        # Check if msg is in json format, if not decode as str
        if b'{' in msg and b'}' in msg:
            msg = ujson.loads(msg)
        else:
            msg = msg.decode()

        if topic == self.publish_success_topic:
            if msg == '':
                print('Operation successful\n')
            else:
                print('Operation successful with return code: {}\n'.format(msg))
        elif topic == self.publish_error_topic:
            status_code = msg['statusCode']
            reason = msg['reasonPhrase']
            print('Operation failed with error code: {} - reason: {}\n'.format(
                status_code, reason
            ))
        else:
            print('On topic: {} received msg: {}'.format(topic, msg))

    def device_configuration(self):
        pass

    def publish_data(self, data):
        wireless_controller, mqtt_communicator = utils.get_wifi_and_cloud_handlers(
            sync_time=False
        )

        result = mqtt_communicator.set_callback(self.receive_message)
        if not result:
            logging.error(
                "Error subscribing to topics with MQTT in publish_data()")

        # TODO: Certificates?

        logging.debug("data to send = {}".format(data))
        result = mqtt_communicator.publish_message(
            payload=data, topic=config.cfg.kaa_topic, qos=config.cfg.QOS
        )

        # TODO: Do we need to wait here for confirmation from receive_message method?
        # Boolean flag or sleep for a while may be needed if the following
        # code returns error even though working connection is established
        if not result:
            logging.error(
                "Does publish return result for KAA?? (MQTT in publish_data())")

        mqtt_communicator.disconnect()
        wireless_controller.disconnect_station()
