# Create cloud infrastructure and deploy packages
This module can be used for building infrastructure for iot-project on the AWS. 
It's also responsible for deployment process of cloud software.

## What is Terraform
Terraform is a tool for building, changing, and versioning infrastructure safely and efficiently. 
Terraform can manage existing and popular service providers as well as custom in-house solutions. 
Configuration files describe to Terraform the components needed to run a single application or your entire datacenter.  
_(via: https://www.terraform.io/intro/index.html)_

## Requirements
### Terraform
Terraform can be installed in two ways:

- You can download terraform binary from this [website](https://www.terraform.io/downloads.html). Downloaded file should be placed in this directory (iot-starter/terraform)
- You can install terraform via package manager on Unix like systems (assuming it’s available). Fedora has the latest version available, so to install it on the Fedora Linux follow this [link](https://www.terraform.io/docs/cli/install/yum.html)

You can check your installation with this command (if the terraform was downloaded as a binary file, remember to run this command from "iot-starter/terraform" directory):

* For Linux:
  ```bash
  terraform --version
  ```

* For Windows:
  ```bash
  terraform.exe -version
  ```

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

### Node.js, npm
These requirements are needed to build and bundle visualization. Nodejs can be installed in two ways:
- From the [website](https://nodejs.org/en/download). Npm should be installed automatically along with nodejs.
- Via the package manager. For Fedora, to install both packages execute the following command:

  ```bash
  sudo dnf install nodejs
  ```

Please remember that in case of using **Windows** during installation of nodejs, it is required to check: **"Automatically install the necessary tools"** which will install Chocolatey on your computer.
You can check if installation succeed with these commands:

```bash
node --version
npm --version
```

Project requires to install node.js in version >= 10.0.
To update npm to the latest version:

```bash
npm install -g npm@latest
```

or to update to the most recent release:

```bash
npm install -g npm@next
```

If you are on **Windows** then you must take additional steps. Run **cmd** with administrative privileges and run three below commands:
(They may take some time)

```
npm install --global --production windows-build-tools@4.0.0
npm config set python python2.7
```

Next you need to set the path for MSBuild.exe. The location of this file may vary. Usually this file resides in:

"C:\Program Files (x86)\Microsoft Visual Studio\2017\BuildTools\MSBuild\XX.X\Bin\MSBuild.exe"

or:

"C:\Program Files (x86)\Microsoft Visual Studio\2015\BuildTools\MSBuild\XX.X\Bin\MSBuild.exe"

Where **XX.X** is a version and may also vary.
If you found the file in 2017 type (remember to change XX.X value!):

```
npm config set msvs_version 2017
npm config set msbuild_path "C:\Program Files (x86)\Microsoft Visual Studio\2017\BuildTools\MSBuild\XX.X\Bin\MSBuild.exe"
```

If it's the latter, change 2017 to 2015 in above commands.

## Installation

### 1. Create virtual environment:
First, you need to create virtual environment (either with python venv module or anaconda-python):

* For anaconda (either in terminal - Linux or anaconda prompt - Windows):
  ```
  cd scripts
  conda create --name ENV_NAME python=3.7 pip
  ```

* For venv:
  * Linux:
  ```
  cd terraform/scripts
  python3 -m venv ENV_NAME
  ```

  * Windows:
  ```
  cd terraform/scripts
  python -m venv ENV_NAME
  ```

where "ENV_NAME" is the name of the environment you’re creating.

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
```
pip install pyserial cryptography click future pyelftools setuptools
pip install -r requirements.txt
```
### 3. Configure aws credentials:

1. Prepare `ACCESS_KEY` and `SECRET_KEY`, which can be obtained from AWS IAM console. Download AWS CLI from 
   https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html to connect AWS with your account and
   run following command:  
```
aws configure
```
If you have trouble generating 'credentials' see the Additional Information and Help section.

### 4. Adjust terraform settings:
You need to create your own s3 bucket in AWS. The whole procedure was described
in this website: https://docs.aws.amazon.com/AmazonS3/latest/user-guide/create-bucket.html

Next, you should change "_bucket_" value to the name of the created bucket
for s3 backend in **main.tf** in **terraform** directory. 
(AWS policy says that s3 bucket name should be unique in the world).
Value "_region_" refers to one of AWS regions. Remember to change "_region_" according to region 
where you have set your s3 bucket.

```
terraform {
  backend "s3" {
    bucket = "YOUR_BUCKET_NAME"
    key = "mobile-iot.wizzdev.tfstate"
    region = "eu-west-2"
  }
}
```

### 5 Modify project variables
Due to security reasons you have to modify files `devel.tfvars` (developement environment settings) and `production.tfvars` (production environment settings) in the `terraform/environments` directory. 
Changing **ESP_HARD_LOGIN, ESP_HARD_PASSWORD, owner and project** values is obligatory. 
Otherwise, your AWS infrastructure could be accessed by unauthorized devices. 

- Values of "ESP_HARD_LOGIN" and "ESP_HARD_PASSWORD" are independent from the AWS account and should be unique - a new connection is created with these credentials.

- "project" variable value should be unique for each infrastructure building.

- Region of S3 bucket created for Terraform state synchronization is independent of these settings and so you can change the "region" variable according to your preferences. All available regions are listed on this webpage: (https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.RegionsAndAvailabilityZones.html) 

Example:

```
mode = "production"
project = "my-mobile-iot"
region = "eu-central-1"
owner = "your_email_adrress"
ESP_HARD_PASSWORD = "TopSecretPassword"
ESP_HARD_LOGIN = "TopSecretLogin"
```

### 6. Initialize terraform, from directory ./terraform run following commands:
(Remember to adjust this command depending on your terraform installation!)

```
terraform init
terraform workspace new production
```
You can also configure `devel` workspace, that can be used for testing and trying new modifications.

## How to run
Here is a short instruction about how to build your cloud infrastructure for this project.

### 1. Set system environment variable for production (or devel)
* Linux:
```
export VERSION="production";
```
* Windows:
```
set VERSION=production
```

### 2. Build deploying packages for Lambdas, REST API and Visualization
```
cd scripts
python build_all.py
cd ..
```

### 3. Run terraform

For **Linux** type **$VERSION** instead of **%VERSION%**

```                                                                        
terraform workspace select %VERSION%
terraform apply -var-file=./environments/%VERSION%.tfvars
```

### 4. Refresh IoT Core Rule in AWS console
Since Terraform's communication with AWS is not 100% perfect, 
the following steps are necessary when first establishing a cloud architecture:   
1. Go to AWS console.
2. Choose IoT Core service from the menu.      
3. Select  Act/Rules and then choose the existing rule on "Edit".     
4. Change SQL version to another, then save. After that, restore the first value and save again.

The above steps are primarily needed when the readings sent to AWS do not appear in the visualization

## Troubleshooting
If any problems occur, please rerun terraform.
Another solution to deal with errors is to destroy terraform and build again. 

## Additional information and help
### Obtaining `ACCESS_CODE` and `SECRET_CODE` from the AWS
You need to gain programmatic access to your AWS account from the computer if you want to automatically build your infrastructure with terraform.
To do that:
1. Go to: https://aws.amazon.com/console/ > IAM service (Identity and Access Management) > Users.
2. Find your name and click on it. You should be redirected to a detailed view of your account.
3. Switch to "Security credentials tabs".
4. Click on the "Create access key" button.
5. Remember both keys because the secret key will not be able to get the secret key from AWS system.
