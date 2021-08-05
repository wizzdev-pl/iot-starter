### Requirements
- Created virtual environment
- User added to dialup group
- Configured chosen cloud


## Activate virtual environment.

```
cd Micropython
```

This step is platform dependent:
#### Windows
* For anaconda:
    ```
    conda activate ENV_NAME
    ```

* For venv:
    ```
    ../ENV_NAME/Scripts/activate.bat
    ```

#### Linux/ Mac OS
* For anaconda:
    ```
    conda activate ENV_NAME
    ```

* For venv:
    ```
    source ../ENV_NAME/bin/activate
    ```

### To develop in PyCharm:

Open the project MicroPython with PyCharm and mark *src* and *ulib_mocks* directory as Sources Root in Pycharm.

## Cloud service provider: 

### - KAA
Make sure that your KAA cloud is configured. For more information please go to README in "KAA" directory [here](../KAA/README.md).

By now, you should have for things:
 - application version
 - device endpoint
 - username
 - password


### - AWS
Make sure that your AWS cloud is configured. For more information please go to 
README in "terraform" directory [here](../terraform/README.md).

If you already have configured AWS infrastructure, make sure that:
- terraform exists either in ".terraform" directory or installed through the package manager
- you have configured ssh connections with AWS (aws configure)


### Basic Setup of the ESP32
To set up a new board or flash the old one. <br>
Make sure that your cloud is configured and in case of using **AWS** make sure that your computer has AWS credentials.


### Flashing the board
Make sure that your board is connected to the computer and you have activated your virtual environment. 
Check the port number - on Linux system, port can be checked through the simple script which will list all usb devices and their ports:

```bash
#!/bin/sh

for sysdevpath in $(find /sys/bus/usb/devices/usb*/ -name dev); do
    (
        syspath="${sysdevpath%/dev}"
        devname="$(udevadm info -q name -p $syspath)"
        [[ "$devname" == "bus/"* ]] && exit
        eval "$(udevadm info -q property --export -p $syspath)"
        [[ -z "$ID_SERIAL" ]] && exit
        echo "/dev/$devname - $ID_SERIAL"
    )
done
```

After finding the correct port, execute:

```bash
python scripts/upload_all.py -p <port> -c <cloud>
```
where \<cloud\> is your chosen cloud service provider (KAA or AWS).<br>
After flashing the board please reset it using button EN button.


### Configuring board network 
Connect to the WiFi network created by a board. Network SSID will be:
```
WizzDev_IoT_<board_id>
```
For example:
```
Wizzdev_IoT_8caab5b8c18c
```
Network is open, so password will not be necessary. After successfull connection,
please open your web browser and type in the Address Bar:
```
http://192.168.4.1/web_pages/setup.html
```
Next, type your WiFi network credentials into SSID and Password fields and press "Submit" button. Remember that this network should have an internet connection. Otherwise, data will not be sent to the cloud. <br>
If you’ve lost connection after submitting, don’t worry - that is supposed to happen.

### Logs from the device
If you want to see logs from working device you should access serial port 
communication with board. We recommend you programs listed below.

### Linux
On Linux you can use picocom:

* Ubuntu:
```bash
sudo apt-get install picocom 
```

* Fedora:
```bash
sudo dnf install picocom 
```

To run:
```bash
picocom <port> --baud 115200
```

### Windows 
On Windows you can use PuTTy _(https://www.putty.org/)_

After installing connect to the device through:
1. Select Session in Category
2. Select Serial in Connection type
3. Type in correct port (Serial line) and speed
4. Open connection

### Mac 
On Mac you can also use picocom
