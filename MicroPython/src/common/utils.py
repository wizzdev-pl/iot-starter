import esp32
import gc
import logging
import machine
import ntptime
import uos
import utime

from communication import wirerless_connection_controller
from communication.wirerless_connection_controller import \
    WirelessConnectionController
from data_upload.mqtt_communicator import MQTTCommunicator
from common import config

TIME_EPOCH_SHIFT = 946684800000
NUMBER_OF_NTP_SYNCHRONIZATION_ATTEMPTS = 5


class ConnectionError(Exception):
    pass


def button_irq(p: machine.Pin) -> None:
    """
    Callback of interrupt of BOOT button. Resets ESP.
    :param p: BOOT pin.
    :return: None
    """
    logging.debug("=== RESET BUTTON PRESSED ===")
    config.ESPConfig.save()
    machine.reset()


def reset_config(p: machine.Pin) -> None:
    """
    Callback of interrupt of button on GPIO32. Resets configuration of ESP (config.json changes to default one).
    :param p: GPIO32 pin.
    :return: None
    """
    logging.debug("=== CONFIG BUTTON PRESSED ===")
    config.cfg.ap_config_done = False
    config.cfg.tested_connection_cloud = False
    config.ESPConfig.save()
    machine.reset()


def init() -> None:
    """
    Initialize ESP, reads or creates configuration, sets interrupts.
    :return: None
    """
    logging.debug("config.py/init()")
    config.cfg = config.ESPConfig()
    config.cfg.load_from_file()

    button = machine.Pin(0, machine.Pin.IN, machine.Pin.PULL_UP)
    button.irq(trigger=machine.Pin.IRQ_FALLING, handler=button_irq)
    esp32.wake_on_ext0(pin=button, level=False)

    button2 = machine.Pin(32, machine.Pin.IN, machine.Pin.PULL_UP)
    button2.irq(trigger=machine.Pin.IRQ_FALLING, handler=reset_config)
    esp32.wake_on_ext0(pin=button2, level=esp32.WAKEUP_ALL_LOW)

    logging.debug("Configuration loaded")


def time_print() -> None:
    """
    Print local time of ESP.
    :return: None
    """
    time = utime.localtime()
    logging.info(
        "Actual time: {}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(time[0], time[1], time[2], time[3], time[4],
                                                                    time[5]))


def get_ntp_time() -> bool:
    """
    Get actual time via NTP.
    :return: Error code (True -> OK, False -> Error).
    """
    logging.debug("utils.py/get_ntp_time()")
    ntptime.host = "3.pl.pool.ntp.org"
    time_before = get_current_timestamp_ms()

    try:
        ntptime.settime()
        time_after = get_current_timestamp_ms()
        print("Sync finished successful time before {} time after {}".format(
            time_before, time_after))
        return True
    except:
        time_after = get_current_timestamp_ms()
        print("Sync finished unsuccessful time before {} time after {}".format(
            time_before, time_after))
        return False


def synchronize_time() -> bool:
    """
    Synchronize time with help of NTP Server.
    :return: Error code (True -> OK, False -> Error).
    """
    logging.debug("utils.py/synchronize_time()")
    i = 0
    while i < NUMBER_OF_NTP_SYNCHRONIZATION_ATTEMPTS:
        result = get_ntp_time()
        if result:
            return True
        i += 1

    raise Exception("Did not synchronize time")


def get_current_timestamp_ms() -> int:
    """
    Get current timestamp in UNIX notation.
    :return: Value of timestamp.
    """
    return int(round(utime.time() * 1000 + (utime.ticks_ms() % 1000) + TIME_EPOCH_SHIFT))


def check_if_file_exists(path_to_file: str) -> int:
    """
    Checks if given file exists. Function check size of given file.
    :param path_to_file: Path to file to check.
    :return: Size of given file.
    """
    logging.debug("utils.py/check_if_file_exists({})".format(path_to_file))
    try:
        return uos.stat(path_to_file)[6]
    except OSError:
        logging.error("No setup file: {}".format(path_to_file))
        return 0


def read_from_file(file_path: str) -> (bool, str):
    """
    Return content of given file.
    :param file_path: Path to file to read from.
    :return: Error code (False -> no such file, True -> file exists), file content (if no file message is returned).
    """
    logging.debug("utils.py/read_from_file({})".format(file_path))
    result = check_if_file_exists(file_path)
    if not result:
        return False, "File not found"
    with open(file_path, 'r') as f:
        data = f.read()
        return True, data


def get_wifi_and_cloud_handlers(sync_time: bool = False) -> (WirelessConnectionController, MQTTCommunicator):
    """
    Creates and returns connection handler to wifi and cloud.
    :param sync_time: flag if time is synchronized.
    :return: Error code (False - error, True - OK), error message, wifi and MQTT handlers.
    """
    logging.debug("utils.py/connect_to_wifi_and_cloud({})".format(sync_time))
    wireless_controller = wirerless_connection_controller.get_wireless_connection_controller_instance()

    try:
        connect_to_wifi(wireless_controller,
                        config.cfg.access_points, sync_time)
        if config.cfg.wifi_connection_failed:
            logging.debug("Resetting due to previous problem with WIFI connection")
            config.cfg.wifi_connection_failed = False
            config.cfg.save()
            machine.reset()
        mqtt_communicator = MQTTCommunicator(cloud_provider=config.cfg.cloud_provider,
                                             timeout=config.cfg.mqtt_timeout)

        while not wireless_controller.sta_handler.isconnected():
            utime.sleep_ms(1)

        mqtt_communicator.connect()
    except Exception as e:
        logging.error("Error get_wifi_and_cloud_handlers(): {}".format(e))
        try:
            mqtt_communicator.disconnect()
        except Exception:
            logging.error("Error in disconnecting MQTT communicator")
        try:
            wireless_controller.disconnect_station()
        except Exception:
            logging.error("Error in disconnecting WiFi controller")

        logging.debug("Unable to publish data. Retrying in {}ms".format(
            config.cfg.data_publishing_period_in_ms))
        config.cfg.wifi_connection_failed = True
        config.cfg.save()
        machine.deepsleep(config.cfg.data_publishing_period_in_ms)

    return wireless_controller, mqtt_communicator


def connect_to_wifi(wireless_controller: WirelessConnectionController, wifi_credentials: list[dict],
                    sync_time: bool = False) -> None:
    """
    Connects ESP to wifi.
    :param wireless_controller: Wifi handler
    :param wifi_credentials: list of ssid & password pairs
    :param sync_time: flag if time is synced.
    :return: None
    """
    logging.debug("utils.py/connect_to_wifi({})".format(sync_time))
    wireless_controller.setup_station(access_points=wifi_credentials)
    gc.collect()
    try:
        wireless_controller.configure_station()
    except Exception as e:
        logging.info("Failed to connect to wifi - {}".format(e))
        try:
            wireless_controller.disconnect_station()
        except Exception:
            pass
        raise ConnectionError(e)

    if sync_time:
        try:
            synchronize_time()
        except Exception as e:
            raise Exception(e)


def print_reset_wake_state() -> (int, int):
    """
    Gets cause of reset and wake and prints that on STDOUT.
    :return: reset and wake cause.
    """
    logging.debug("utils.py/print_reset_wake_state()")
    reset = machine.reset_cause()
    wake = machine.wake_reason()
    reset_cause = ''
    wake_cause = ''

    if reset == machine.PWRON_RESET:
        reset_cause = 'Power On Reset'
    elif reset == machine.HARD_RESET:
        reset_cause = 'Hard Reset'
    elif reset == machine.WDT_RESET:
        reset_cause = 'Watchdog Timer Restart'
    elif reset == machine.DEEPSLEEP_RESET:
        reset_cause = 'Deep sleep reset'
    elif reset == machine.SOFT_RESET:
        reset_cause = 'Soft Reset'
    logging.debug("Reset Cause = %s" % reset_cause)

    if wake == machine.PIN_WAKE:
        wake_cause = "Pin Wake up"
    elif wake == machine.TOUCHPAD_WAKE:
        wake_cause = 'Touch Wake up'
    elif wake == machine.ULP_WAKE:
        wake_cause = 'Coprocessor wake up'
    elif wake == machine.EXT0_WAKE:
        wake_cause = 'Single RTC_GPIO wake up'
    elif wake == machine.EXT1_WAKE:
        wake_cause = 'Multi RTC_GPIO wake up'
    elif wake == machine.TIMER_WAKE:
        wake_cause = 'Timer wake up'

    logging.debug("Wake Cause = %s" % wake_cause)
    return reset, wake
