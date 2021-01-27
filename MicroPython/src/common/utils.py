import ntptime
import utime
import uos
import machine
import ujson
import logging

from data_upload.mqtt_communicator import MQTTCommunicator
from communication import wirerless_connection_controller
from common import config

TIME_EPOCH_SHIFT = 946684800000  # in ms - embedded port of Unix time counts from year 2000, not 1970
NUMBER_OF_NTP_SYNCHRONIZATION_ATTEMPTS = 5


# Print local time on ESP32 as human readable string
def time_print():
    time = utime.localtime()
    logging.info("Actual time: {}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(time[0], time[1], time[2], time[3], time[4], time[5]))


def sync_time_with_ntpserver():
    logging.debug("utils.py/sync_time_with_ntpserver()")
    # TODO: check if time was actually synced
    ntptime.host = "3.pl.pool.ntp.org"
    try:
        time_before = get_current_timestamp_ms()
        ntptime.settime()  # get current time from ntp server
        time_after = get_current_timestamp_ms()
        print("Sync finished successful time before {} time after {}".format(time_before, time_after))
        return True
    except:
        time_after = get_current_timestamp_ms()
        print("Sync finished unsuccessful time before {} time after {}".format(time_before, time_after))
        return False


def synchronize_time():
    logging.debug("utils.py/synchronize_time()")
    i = 0
    while i < NUMBER_OF_NTP_SYNCHRONIZATION_ATTEMPTS:
        result = sync_time_with_ntpserver()
        if result:
            return True
        i += 1
    return False


def get_current_timestamp_ms():
    return int(round(utime.time() * 1000 + (utime.ticks_ms() % 1000) + TIME_EPOCH_SHIFT))


def get_time_str():
    logging.debug("utils.py/get_time_str()")
    t = utime.ticks_ms()
    return '%.3f' % (t/1000)


def check_if_file_exists(path_to_file: str):
    logging.debug("utils.py/check_if_file_exists({})".format(path_to_file))
    try:
        return uos.stat(path_to_file)[6]
    except OSError:
        return False


def set_ap_config_done(done: bool):
    logging.debug("utils.py/set_ap_config_done({})".format(done))
    file_path = 'config.json'
    config_dict = {}
    with open(file_path, "r", encoding="utf8") as infile:
        config_dict = ujson.load(infile)
    config_dict['AP_config_done'] = done
    with open(file_path, "w", encoding="utf8") as infile:
        ujson.dump(config_dict, infile)


def restore_ap_mode():
    logging.debug("utils.py/restore_ap_mode()")
    touch = machine.TouchPad(machine.Pin(14))
    threshold = 300
    for i in range(50):
        if touch.read() > threshold:
            return
        else:
            utime.sleep(0.1)
    print("Reseting to AP mode!")
    set_ap_config_done(False)
    led = machine.Pin(2, machine.Pin.OUT)
    led.on()
    utime.sleep(1)
    led.off()


def read_from_file(file_path):
    logging.debug("utils.py/read_from_file({})".format(file_path))
    result = check_if_file_exists(file_path)
    if not result:
       return False, "File not found"
    with open(file_path, 'r') as f:
        data = f.read()
        return True, data


def create_MQTT_communicator_from_config():
    logging.debug("utils.py/create_MQTT_communicator_from_config()")
    return MQTTCommunicator(use_AWS=config.cfg.use_aws,
                            client_id=config.cfg.aws_client_id,
                            endpoint=config.cfg.aws_endpoint,
                            port=config.cfg.mqtt_port_ssl,
                            timeout=config.cfg.mqtt_timeout)


def connect_to_wifi_and_AWS(sync_time=False):
    wireless_controller = wirerless_connection_controller.get_wireless_connection_controller_instance()
    logging.info("Connect to wifi and aws in if")
    connect_to_wifi(wireless_controller, sync_time)
    mqtt_communicator = create_MQTT_communicator_from_config()

    result = mqtt_communicator.connect()
    if not result[0]:
        logging.info("Failed to connect to mqtt server! {}".format(result[1]))
        try:
            mqtt_communicator.disconnect()
        except:
            pass
            # Probably not connected ignore

        try:
            wireless_controller.disconnect_station()
        except:
            # Probably not connected ignore
            pass

        return result[0], result[1], None, None

    return True, "", wireless_controller, mqtt_communicator


def connect_to_wifi(wireless_controller, sync_time=False):
    logging.debug("utils.py/connect_to_wifi_and_AWS({})".format(sync_time))
    wireless_controller.setup_station(ssid=config.cfg.ssid, password=config.cfg.password)

    try:
        result = wireless_controller.configure_station()
    except Exception as e:
        logging.info("Failed to connect to wifi {}".format(e))
        return False, "Failed to connect to wifi", None, None

    print(result)
    logging.debug("After configure station")
    if not result[0]:
        logging.info("Failed to connect to wifi!")
        try:
            wireless_controller.disconnect_station()
        except:
            # Probably not connected ignore
            logging.debug("Not connected except")
            pass
        return result[0], result[1], None, None
    logging.debug("After disconnect station")

    if sync_time:
        result = synchronize_time()
        if not result:
            return result, "Failed to synchronize time with ntp server", None, None


def get_last_commit_info():
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


def print_reset_wake_state():
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


def flash_blue_led(published_success):
    logging.debug("utils.py/flash_blue_led({})".format(published_success))
    blue_led_pin = machine.Pin(config.cfg.blue_led_pin, machine.Pin.OUT)

    if published_success:
        blue_led_pin.on()
        utime.sleep(0.1)
        blue_led_pin.off()
    else:
        blue_led_pin.on()
        utime.sleep(0.07)  # 0.07s blinking is more visible
        blue_led_pin.off()
        utime.sleep(0.07)
        blue_led_pin.on()
        utime.sleep(0.07)
        blue_led_pin.off()
