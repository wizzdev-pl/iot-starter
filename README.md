# WizzDev Mobile IoT Platform

## Overview
This repository contains the WizzDev mobile IoT application in the "Starter" version. The project is based on ESP32 MCU and one of supported cloud service providers infrastructure. ESP32 is responsible for gathering data from the sensor (in this case DHT22), with a specified period of time, and sending them to the chosen cloud using the MQTT protocol. Depending on the chosen cloud, data can be viewed:

- AWS: directly on the AWS, or on the dedicated visualization page.
- KAA: directly on the Kaa on the created dashboard for a device.
- ThingsBoard: directly on the dashboard in ThingsBoard local page

The board was programmed using MicroPython, which is a Python implementation for embedded devices. If you are a novice and / or just want to try a solution that works without putting much work into it, we recommend using Kaa cloud which is much faster to set up.


## Prerequisites
Before building there are some packages required to install on the PC. Run the following command to install them (note that there is also a possibility to use [anaconda-python](https://www.anaconda.com/products/individual) virtual environment instead of python3-virtualenv. If one chooses so, then there is no need to install: “python3-virtualenv” and “python-setuptools”):

* Ubuntu:

```
sudo apt-get install git wget bison gperf python python-pip python3-virtualenv python-setuptools python-serial python-click python-cryptography python-future python-pyparsing python-pyelftools ninja-build libssl-dev
```

* Fedora like systems:

(Tested on Fedora 33, should also work at major versions 30+ at least.)

```
sudo dnf install git wget bison gperf python python-pip python3-virtualenv python-setuptools pyserial python-click python-cryptography python-future python-pyparsing python-pyelftools ninja-build openssl-devel
```

* Windows:

    - install [git](https://git-scm.com/downloads)
    - install [python](https://www.python.org/downloads/windows/) (3.6 / 3.7) with pip and virtualenv - no need to install if you've chosen anaconda-python
    - install drivers for ESP32 from this [link](https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers) - make sure to select Universal WIndows Driver

Make sure you have access to required hardware:

- **(For AWS only)** Account with ACCESS_CODE and SECRET_CODE - [more info](https://github.com/wizzdev-pl/iot-starter/blob/devel/terraform/README.md#Additional-information-and-help)
- ESP32 MCU board (preferably ESP32 DevKitC v4)
- MicroUSB cable
- DHT11 or DHT22 sensor with cables (additional 10k pull-up resistor may be needed) or BME280
- WiFi connection


## Cloning repository

To clone repository use following lines:

```bash
git clone https://github.com/wizzdev-pl/iot-starter.git
cd iot-starter
git submodule init
git submodule update --init --recursive
```

* Linux users:

To flash and debug device it is required to add user to dialout group:

```
sudo usermod -a -G dialout $USER
```
*Note that in some cases a logout is required 

---

## Installing
Depending on your cloud service provider: 

### **KAA configuration:**
KAA configuration is easy to set up and work with cloud. Detailed description of this procedure is available in the "KAA" directory [here](KAA/README.md).

### **AWS configuration:** 
AWS's configuration is handled using terraform. Detailed description of this procedure is available in the "terraform" directory [here](terraform/README.md).

### **ThingsBoard configuration:** 
As ThingsBoard is hosted locally on your device you need to install it first. Detailed description of the whole procedure is available in "ThingsBoard" directory [here](ThingsBoard/README.md)

---
## **After cloud setup:**

### Flashing the board 
A dedicated Python script was prepared for this procedure. For more information, please go to the "MicroPython" directory [here](MicroPython/README.md).

---

## Working with configured device
After all these steps, the board should send data from the sensor into the chosen cloud. Depending on your choice of cloud service provider, you can:

## **For KAA:**

### Device management

Log in to your KAA account. From the side pane select "Device management" -> "Devices". Click on your device and there you should see the "Device telemetry" time series plot where data is shown. Legend should show two colorful dots "auto-dht_h" and "auto-dht_t" which are respectively humidity and temperature.

### Dashboard

Another way of visualization of the data is to create a dashboard. You can use already created widgets or create custom ones. For more information visit [documentation](https://docs.kaaiot.io/KAA/docs/v1.3.0/Features/Visualization/WD/Dashboards/).

## **For ThingsBoard:**

### Device management

Log in to your ThingsBoard page and from the side pane select the "Devices" tab. Click on your device and select "Latest telemetry", there should be shown the latest telemetry sent to cloud. In the "Details" you can manage your device credentials set during the device registering or assign device to customer. In the "Attributes" select "Server attributes" in "Entity attributes scope", here you can manage created attributes. After first connection a variable SleepTime should be created. If not, make sure all passed ThingsBoard credentials are correct. SleepTime represents frequency of sending data to cloud in seconds, you can change the variable directly from attributes tab or create a special widget in your dashboard.

### Dashboard

To visualize data you need to create a dashboard. Whole process of setting up dashboard is described [here](https://thingsboard.io/docs/user-guide/dashboards/). In order to change your SleepTime attribute from dashboard, you need to click on the "Add new widget" button in the right bottom corner, then: "Create new widget" -> "Input widgets" -> "Update server integer attribute". Add datasource and as an attribute select SleepTime. In the widget settings change its title, in the "Advanced" tab add error message and set "Min value" to 30(seconds). Smaller value may cause software problems.

---

## **For AWS:**

### AWS console - IoT Core
Log in to your AWS account. Go to 'IoT Core' service. Next, choose "Test" and into "Subscription topic" type:
```
topic/data
```
Finally, click "Subscribe to topic". After some time you should see dataframes send by ESP32 board. 

### Visualization page
WizzDev prepares a more convenient way to view data - a dedicated visualization webpage.
Visualization page url is generated by AWS during infrastructure build. So the URL is connected with your AWS account.<br>
You can find this URL in places listed below:

- in file MicroPython/src/aws_config.json as **visualization_url**
- in the "CloudFront" service on your AWS account under the **Domain Name** field

Using this page you can find charts of temperature and humidity for all devices registered to your AWS account. If you click on a specified device on the "All devices" list, you will be able to see a chart with data only from this device.
