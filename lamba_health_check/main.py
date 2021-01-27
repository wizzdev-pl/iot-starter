import logging
import datetime
import os

import boto3

from checks import is_any_battery_status_was_sent_recently, is_any_measurement_was_sent_recently, is_visualization_okay


def main(*args, **kwargs):
    logging.info("Datetime: ", datetime.datetime.utcnow().strftime("%d/%m/%y %H:%M:%S"))
    if not is_any_battery_status_was_sent_recently():
        raise Exception("Check failed: " + is_any_battery_status_was_sent_recently.__name__)
    if not is_any_measurement_was_sent_recently():
        raise Exception("Check failed: " + is_any_measurement_was_sent_recently.__name__)
    if not is_visualization_okay("https://iot-demo.wizzdev.pl"):
        raise Exception("Check failed: " + is_visualization_okay.__name__)
