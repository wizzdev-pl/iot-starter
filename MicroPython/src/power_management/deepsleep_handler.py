# TODO: importowac tylko to co potrzebne
from logging import debug, error, info
from machine import deepsleep
from common import config, utils
from common.utils import get_current_timestamp_ms
from peripherals.dht_sensor import DHTSensor


# Get actual time from server
# TODO: uproscic to, skorzystac z funkcji utils.synchronize_time()
def get_time_from_ntp():
    debug("get_time_from_aws()")
    result, error_msg, wireless_controller, mqtt_communicator = utils.connect_to_wifi_and_AWS(sync_time=True)

    if not result:
        error("Error in get_time_from_aws(), result={}".format(result))
        # data_recorder.errors_new('Error conneceting to mqtt server at power_on_action {}'.format(error_msg), utils.get_current_timestamp_ms())
        # deepsleep(config.FAILED_TO_SYNCHRONIZE_TIME_TIMEOUT_IN_MS)
    else:
        mqtt_communicator.update_device_shadow_startup(utils.get_current_timestamp_ms())
        mqtt_communicator.disconnect()
        wireless_controller.disconnect_station()


# Transfer JSON message with sensor readings to AWS cloud
def publish_to_aws(data):
    debug("publish_to_aws()")
    result, error_reason, wireless_controller, mqtt_communicator = utils.connect_to_wifi_and_AWS(sync_time=False)

    # TODO: trzeba to przerobic by dzialalo bez karty SD
    if not result:
        error("utils.connect_to_wifi_and_AWS: {}".format(error_reason))
        # data_recorder.errors_new(error_reason, utils.get_current_timestamp_ms())
        return

    mqtt_communicator.get_device_shadow(timeout_ms=5000)

    # TODO: trzeba to przerobic by dzialalo bez karty SD
    # result = mqtt_communicator.publish_errors()
    # if not result:
    #     error("Error: mqtt_communicator.publish_errors() = {}".format(result))
        #    data_recorder.errors_new('Error publishing error log to MQTT in send_data()',
        #                             utils.get_current_timestamp_ms())
    # else:
    #    data_recorder.errors_clear()

    debug("data to send = {}".format(data))
    info(config.cfg.aws_topic)
    result = mqtt_communicator.publish_message(payload=data, topic=config.cfg.aws_topic, qos=config.cfg.QOS)

    # TODO: trzeba to przerobic by dzialalo bez karty SD
    if not result:
        error("'Error publishing data to MQTT in send_data()'")
        # data_recorder.errors_new('Error publishing data to MQTT in send_data()', utils.get_current_timestamp_ms())
    # else:
    #    if deepsleep_dict != {} and number_of_samples_to_send_dht == 0:
    #        data_recorder.clear_sample_storage()

    # flash the LED according to publish success
    info("Blink led {}".format(config.cfg.blink_led))
    if config.cfg.blink_led:
        utils.flash_blue_led(result)

    mqtt_communicator.disconnect()
    wireless_controller.disconnect_station()


# Perform all sensor operations - power up, measure, power down
# Returns measured data as JSON that is ready to be uploaded to AWS
def measure():
    debug("measure(), reading data from sensor: {}".format(config.cfg.dht_type))
    sensor = DHTSensor(config.cfg.dht_type, config.cfg.dht_measurement_pin, config.cfg.dht_power_pin)
    sensor.turn_on()
    sensor.measure()
    sensor.turn_off()

    json = dict()
    json['dht_t'] = [[get_current_timestamp_ms(), sensor.temperature()]]
    json['dht_h'] = [[get_current_timestamp_ms() + 1, sensor.humidity()]]
    return json


# Sleep CPU. After the input time is over, CPU starts program execution from the beginning
def power_save(ms):
    debug("sleep({})".format(ms))
    ms = int(ms)
    if ms <= 0:
        ms = 10
    deepsleep(ms)
