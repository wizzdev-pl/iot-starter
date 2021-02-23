from logging import debug, error, info
from machine import deepsleep
from common import config, utils
from common.utils import get_current_timestamp_ms
from peripherals.dht_sensor import DHTSensor


def check_connection_to_aws():
    """
    Check if connection to AWS is possible and update shadow time.
    :return: Error code (0 - ok, 1 - error occurred.
    """
    debug("check_connection_to_aws()")
    result, error_msg, wireless_controller, mqtt_communicator = utils.get_wifi_and_aws_handlers(sync_time=True)

    if not result:
        error("Error in get_time_from_aws(), result={}".format(result))
        return 1
    else:
        mqtt_communicator.update_device_shadow_startup(utils.get_current_timestamp_ms())
        mqtt_communicator.disconnect()
        wireless_controller.disconnect_station()

    return 0


def publish_to_aws(data: dict):
    """
    Send data to the cloud.
    :param data: Measurements.
    :return: Error code (0 - ok, 1 - unable to connect, 2 - no data sent).
    """
    debug("publish_to_aws()")
    result, error_reason, wireless_controller, mqtt_communicator = utils.get_wifi_and_aws_handlers(sync_time=False)

    if not result:
        error("utils.connect_to_wifi_and_AWS: {}".format(error_reason))
        return 1

    mqtt_communicator.get_device_shadow(timeout_ms=5000)

    debug("data to send = {}".format(data))
    info(config.cfg.aws_topic)
    result = mqtt_communicator.publish_message(payload=data, topic=config.cfg.aws_topic, qos=config.cfg.QOS)

    if not result:
        error("Error publishing data to MQTT in send_data()")

    mqtt_communicator.disconnect()
    wireless_controller.disconnect_station()

    if not result:
        return 2

    return 0


def power_save(ms):
    """
    Puts ESP to sleep.
    :param ms: Amount of time to sleep in milliseconds.
    """
    debug("sleep({})".format(ms))
    ms = int(ms)
    if ms <= 0:
        ms = 10
    deepsleep(ms)
