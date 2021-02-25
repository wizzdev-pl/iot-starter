import ntptime
import utime
import uos
import machine
import ujson
import logging

from communication.wirerless_connection_controller import WirelessConnectionController
from data_upload.mqtt_communicator import MQTTCommunicator
from communication import wirerless_connection_controller
from common import config

TIME_EPOCH_SHIFT = 946684800000
NUMBER_OF_NTP_SYNCHRONIZATION_ATTEMPTS = 5


def time_print() -> None:
    """
    Print local time of ESP.
    :return: None
    """
    time = utime.localtime()
    logging.info("Actual time: {}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(time[0], time[1], time[2], time[3], time[4], time[5]))


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
        print("Sync finished successful time before {} time after {}".format(time_before, time_after))
        return True
    except:
        time_after = get_current_timestamp_ms()
        print("Sync finished unsuccessful time before {} time after {}".format(time_before, time_after))
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


def get_time_str() -> str:
    """
    Get time as string in seconds (as float with 3 significant digits).
    :return: Value
    """
    logging.debug("utils.py/get_time_str()")
    t = utime.ticks_ms()
    return '%.3f' % (t/1000)


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


def set_ap_config_done(done: bool) -> None:
    """
    Changes AP_CONFIG_DONE in config.json file.
    :param done: Value to change to.
    :return: None.
    """
    logging.debug("utils.py/set_ap_config_done({})".format(done))
    file_path = 'config.json'
    config_dict = {}
    with open(file_path, "r", encoding="utf8") as infile:
        config_dict = ujson.load(infile)
    config_dict['AP_config_done'] = done
    with open(file_path, "w", encoding="utf8") as infile:
        ujson.dump(config_dict, infile)


def restore_ap_mode() -> None:
    logging.debug("utils.py/restore_ap_mode()")
    touch = machine.TouchPad(machine.Pin(14))
    threshold = 300
    for i in range(50):
        if touch.read() > threshold:
            return
        else:
            utime.sleep(0.1)
    set_ap_config_done(False)
    led = machine.Pin(2, machine.Pin.OUT)
    led.on()
    utime.sleep(1)
    led.off()


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


def create_mqtt_communicator_from_config() -> MQTTCommunicator:
    """
    Create new instance od MQTTCommunicator.
    :return: Instance of MQTTCommunicator.
    """
    logging.debug("utils.py/create_MQTT_communicator_from_config()")
    return MQTTCommunicator(use_AWS=config.cfg.use_aws,
                            client_id=config.cfg.aws_client_id,
                            endpoint=config.cfg.aws_endpoint,
                            port=config.cfg.mqtt_port_ssl,
                            timeout=config.cfg.mqtt_timeout)


def get_wifi_and_aws_handlers(sync_time: bool = False) -> (WirelessConnectionController, MQTTCommunicator):
    """
    Creates and returns connection handler to wifi and AWS.
    :param sync_time: flag if time is synchronized.
    :return: Error code (False - error, True - OK), error message, wifi and MQTT handlers.
    """
    logging.debug("utils.py/connect_to_wifi_and_aws({})".format(sync_time))
    wireless_controller = wirerless_connection_controller.get_wireless_connection_controller_instance()

    try:
        connect_to_wifi(wireless_controller, sync_time)
        mqtt_communicator = create_mqtt_communicator_from_config()
        mqtt_communicator.connect()
    except Exception as e:
        logging.error("Error wifi_get_adn_aws_handler(): {}".format(e))
        try:
            mqtt_communicator.disconnect()
        except Exception:
            pass
        try:
            wireless_controller.disconnect_station()
        except Exception:
            pass

        logging.debug("RESETTING BOARD")
        machine.reset()

    return wireless_controller, mqtt_communicator


def connect_to_wifi(wireless_controller: WirelessConnectionController, sync_time: bool = False) -> None:
    """
    Connects ESP to wifi.
    :param wireless_controller: Wifi handler
    :param sync_time: flag if time is synced.
    :return: None
    """
    logging.debug("utils.py/connect_to_wifi({})".format(sync_time))
    wireless_controller.setup_station(ssid=config.cfg.ssid, password=config.cfg.password)

    try:
        wireless_controller.configure_station()
    except Exception as e:
        logging.info("Failed to connect to wifi {}".format(e))
        try:
            wireless_controller.disconnect_station()
        except Exception:
            pass
        raise Exception(e)

    if sync_time:
        try:
            synchronize_time()
        except Exception as e:
            raise Exception(e)


def get_last_commit_info() -> dict:
    """
    Get the most recent committed data.
    :return: Data as dict
    """
    logging.debug("utils.py/get_last_commit_info()")
    file_path = 'commit_info.txt'

    commit_info_dict = {}

    if check_if_file_exists(path_to_file=file_path):
        with open(file_path, 'r', encoding="utf8") as file:
            commit_info_dict = ujson.load(file)
    else:
        commit_info_dict['hash'] = 'Unknown'
        commit_info_dict['tag'] = 'Unknown'
        print("File with hash of the last commit doesn't exist")

    return commit_info_dict


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
