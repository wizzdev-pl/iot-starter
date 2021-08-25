# Set up ThingsBoard locally on your computer
The instruction walks you through the process of creating your own IoT device in just a few steps.

## What is ThingsBoard
ThingsBoard is an open-source IoT platform that enables rapid development, management, and scaling of IoT projects. You can host it locally on your device or use the paid cloud version 

## Requirements

### Python 3, PIP 
Python can be downloaded from this [website](https://www.python.org/downloads) (in case of using [Anaconda environment](https://www.anaconda.com/products/individual), please skip this part and refer to "**Installation**" section). The Python version required for this project is: either 3.6 or 3.7 (preferably). Please follow installation instructions from their website. 
After installation, you can check if it is installed correctly by typing the following commands in your terminal:

* Linux
```bash
python3 --version
pip3 --version
```
If python3 is not recognized, try "python"

* Windows:
```bash
python --version
pip --version
```

## Installation

### 1. Create virtual environment:
First, you need to create virtual environment (either with python venv module or anaconda-python):

Note, that **"ENV_NAME"** is the name of the environment you’re creating.

Enter main directory of the project (iot-starter):
```bash
cd iot-starter
```

* For anaconda (either in terminal - Linux or anaconda prompt - Windows):
  ```
  conda create --name ENV_NAME python=3.7 pip
  ```

* For venv:
  * Linux:
  ```
  python3 -m venv ENV_NAME
  ```

  * Windows:
  ```
  python -m venv ENV_NAME
  ```

Next, you should activate it. This step is platform dependent:
#### Windows
* For anaconda:
  ```
  conda activate ENV_NAME
  ```

* For venv:
  ```
  ENV_NAME/Scripts/activate.bat
  ```

#### Linux/ Mac OS
* For anaconda:
  ```
  conda activate ENV_NAME
  ```

* For venv:
  ```
  source ENV_NAME/bin/activate
  ```

### 2. Install requirements

After you've created virtual environment, your current directory should be "iot-starter"

``` 
pip install pyserial cryptography click future pyelftools setuptools
pip install -r ThingsBoard/requirements.txt
```

## Set up local ThingsBoard server

### 1. Installation

## Linux
To create your own ThingsBoard server on Linux (Ubuntu), just follow this [instruction](https://thingsboard.io/docs/user-guide/install/ubuntu/).

## Windows
For Windows users, instruction can be found [here](https://thingsboard.io/docs/user-guide/install/windows/).

### 2. Device profile set up

Once you finally have your ThingsBoard ready, open your browser and navigate to server webpage. Default link is:
```
http://localhost:8080/
```
Now go ahead and log in to your server. If you have specified *-loadDemo* during execution of the installation script, the default credentials are:
* System Administrator: sysadmin@thingsboard.org / sysadmin
* Tenant Administrator: tenant@thingsboard.org / tenant
* Customer User: customer@thingsboard.org / customer

You can always change passwords for each account in account profile page.

Now the only thing you need to do is obtain two keys needed for device registering. To do this, click on the **Device profiles** tab on the left and hit the profile name you want to use (you can use default one or create a new profile). Toggle on edit mode, then go to **Device provisioning** tab and change the **Provision strategy** to 'Allow to create new devices'. Apply changes and now two new fields have appeared - **Provision device key** and **Provision device secret**. Please copy them and save for later.

### 3. Open ports

To send telemetry data directly from your DevBoard to local server on your computer, you need to open two communication ports.

* Linux:
```
sudo ufw allow 8080
sudo ufw allow 1883
```
* Windows