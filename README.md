# WizzDev Mobile IoT Platform

## Overview
This repository contains the WizzDev mobile IoT application in the "Starter" version.
The project is based on ESP32 MCU and Amazon Web Services infrastructure. ESP32 is responsible for
gathering data from the sensor (in this case DHT22), with a specified period of time, and send them to AWS 
using the MQTT protocol. Data can be viewed directly on the AWS, or on the dedicated visualization page.
The board was programmed using MicroPython, which is a Python implementation
for embedded devices.


## Cloning repository
To clone repository use following lines:
```bash
    git@gitlab.com:wizzdev/internal-projects/iot-starter.git
    cd iot-starter
    git submodule init
    git submodule update --init --recursive
```

## Prerequisites

Before compiling there are some packages required to install on the PC. Run the following command to install them:

```
sudo apt-get install git wget bison gperf python python-pip python-setuptools python-serial python-click python-cryptography python-future python-pyparsing python-pyelftools ninja-build libssl-dev
```

To flash and debug device it is required to add user to dialout group:

```
sudo usermod -a -G dialout $USER
```

- AWS account with ACCESS_CODE and SECRET_CODE
- ESP32 MCU board (preferably ESP32 DevKitC v4)
- MicroUSB cable
- DHT11 or DHT22 sensor with cables (additional 10k pull-up resistor may be needed)
- WiFi connection

## Installing
### AWS configuration 
AWS's configuration is handled using terraform. Detailed description of this 
procedure is available in the ".terraform" directory.

### Flashing the board 
A dedicated Python script was prepared for this procedure. For more information,
please go to the "MicroPython" directory.

## Working with configured device
After all these steps, the board should send data from the sensor into AWS.
There are two ways to check the data from the board.

### AWS console
Log in into your AWS console, go to the "IoT Core" service and choose "Test". 
In the "Subscription topic" field, type "topic/data" and click "Subscribe to topic". 
After some time you should be able to see data sent from the device. 

### Visualization page
WizzDev prepares a more convenient way to view data- a dedicated visualization
webpage. Using this page you can find charts of temperature and humidity for all
devices registered to your AWS account. If you click on a specified device
on the "All devices" list, you will be able to see a chart with data only 
from this device