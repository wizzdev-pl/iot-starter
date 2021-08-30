import argparse
import os

import esptool

# esptool.py --chip esp32 --port "$PORT" erase_flash

MICROPYTHON_BIN_FILE_NAME = "esp32-20210623-v1.16.bin"
MICROPYTHON_BIN_FILE_DIR = "MicroPython_firmware/"
ROOT_DIR = os.path.abspath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), '..'))


# read -n 1 -s -r -p "Reset ESP32 into bootloader mode - Hold BOOT button and click EN button. Release BOOT. Then press any key to continue"
def erase_chip_advanced(port):
    print('Erasing Chip...')
    esp = esptool.ESPLoader.detect_chip(port=port)
    print(f'Detected chip: {esp.get_chip_description()}')

    print("Features: %s" % ", ".join(esp.get_chip_features()))
    print("Crystal is %dMHz" % esp.get_crystal_freq())
    mac = esp.read_mac()
    print(f"MAC: {':'.join(map(lambda x: '%02x' % x, mac))}")

    esp.run_stub()
    esptool.erase_flash(esp, None)

    print('Hard resetting via RTS pin...')
    esp.hard_reset()


def erase_chip(port):
    command = ["--chip", "esp32", "--port", port, "erase_flash"]
    esptool.main(command)


def flash_micropython(port):
    micropython_bin_file_path = os.path.join(
        ROOT_DIR, MICROPYTHON_BIN_FILE_DIR, MICROPYTHON_BIN_FILE_NAME)

    command = ["--chip", "esp32", "--port", port,
               "--baud", "230400", "--after", "hard_reset",
               "write_flash", "-z", "0x1000", micropython_bin_file_path]
    esptool.main(command)


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', metavar='PORT', type=str, required=True,
                        help="Com port of the device")
    args = vars(parser.parse_args())
    return args


if __name__ == '__main__':
    args = parse_arguments()

    erase_chip(args['port'])
    flash_micropython(args['port'])
