# Create cloud infrastructure and deploy packages
This module can be used for building infrastructure for iot-project on the AWS. 
It's also responsible for deployment process of cloud software.

## What is Terraform
Terraform is a tool for building, changing, and versioning infrastructure safely and efficiently. 
Terraform can manage existing and popular service providers as well as custom in-house solutions. 
Configuration files describe to Terraform the components needed to run a single application or your entire datacenter.  
_(via: https://www.terraform.io/intro/index.html)_

## Requirements
#### Terraform
You can download terraform binary from this website: https://www.terraform.io/downloads.html
Downloaded file should be placed in this directory (iot-starter/terraform). You can check your installation with this command:
```bash
terraform --version
```
 
#### Python 3, PIP 
Python can be downloaded from this website: https://www.python.org/downloads/
Please follow installation instructions from their website. 
After installation, you can check if it is installed correctly by typing the following commands in your terminal:
```bash
python3 --version
pip3 --version
```

#### Node.js, npm
These requirements are needed to build and bundle visualization. Nodejs can be installed from this website:
https://nodejs.org/en/download/. Npm should be installed automatically along with nodejs.
You can check if installation succeed with these commands:
```bash
node --version
npm --version
```
Project requires to install node.js in version >= 10.0.
To update npm to the latest version
```bash
npm install -g npm@latest
```
or to update to the most recent release:
```bash
npm install -g npm@next
```


## Installation

##### 1. Create virtual environment:
First, you need to create virtual environment
```
cd scripts
python3 -m venv venv
```
Next, you should activate it. This step is platform dependent
###### Windows
```
venv/Scripts/activate.bat
```

###### Linux/ Mac OS
```
source venv/bin/activate
```

##### 2. Install requirements
```
pip3 install -r requirements.txt
```
##### 3. Configure aws credentials:

1. Prepare `ACCESS_KEY` and `SECRET_KEY`, which can be obtained from AWS IAM console.
Connect AWS with your account by running following command:  
```
aws configure
```
If you have trouble generating 'credentials' see the Additional Information and Help section.

##### 4. Adjust terraform settings:
You need to create your own s3 bucket in AWS. The whole procedure was described
in this website: https://docs.aws.amazon.com/AmazonS3/latest/user-guide/create-bucket.html

Next, you should change "_bucket_" value to the name of the created bucket
for s3 backend in main.tf in this directory. 
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

##### 5 Modify project variables
Due to security reasons you have to modify files `devel.tfvars` (developement environment settings) and `production.tfvars` (production environment settings) in 
the `terraform/environments` directory. Changing **ESP_HARD_LOGIN, ESP_HARD_PASSWORD, owner and project** 
values is obligatory. Other way your AWS infrastructure could be accessed by 
unauthorized devices. 

**Project** variable value, should be unique for each infrastructure 
building.

You can change **Region** variable according to your preferences. All available regions
are listed in this webpage (https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.RegionsAndAvailabilityZones.html)
Region of S3 bucket created for Terraform state synchronization is independent of this settings.

Example:

```
mode = "production"
project = "my-mobile-iot"
region = "eu-central-1"
owner = "your_email_adrress"
ESP_HARD_PASSWORD = "TopSecretPassword"
ESP_HARD_LOGIN = "TopSecretLogin"
```

##### 6. Initialize terraform, from directory ./terraform run following commands:
```
./terraform init
./terraform workspace new production
```
You can also configure `devel` workspace, that can be used for testing and trying new modifications.

## How to run
Here is a short instruction about how to build your cloud infrastructure for this project.

##### 1. Set system environment variable for production (or devel)
on Linux:
```
export VERSION="production";
```
on Windows:
```
set VERSION=production
```

##### 2. Build deploying packages for Lambdas, REST API and Visualization
```
cd scripts
python build_all.py
cd ..
```
##### 3. Run terraform
```                                                                        
./terraform workspace select $VERSION
./terraform apply -var-file=./environments/$VERSION.tfvars                                                                                                                                                              
```
##### 4. Refresh IoT Core Rule in AWS console
Since Terraform's communication with AWS is not 100% perfect, 
the following steps are necessary when first establishing a cloud architecture:   
1. Go to AWS console.
2. Choose IoT Core service from the menu.      
3. Select  Act/Rules and then choose existed rule on "Edit".     
4. Change SQL version to another, then save. After that restore back first value and save again.

The above steps are primarily needed when the readings sent to AWS do not appear in the visualization

## Troubleshooting
If any problems occurs, please rerun terraform.
Another solution to deal with errors is to destroy terraform and build again. 

## Additional information and help
### Obtaining `ACCESS_CODE` and `SECRET_CODE` from the AWS
You need to gain programmatic access to your AWS account from computer if you want to automatically build your infrastructure with terraform.
To do that:
1. Go to: https://aws.amazon.com/console/ > IAM service (Identity and Access Management) > Users.
2. Find your name and click on it. You should be redirected to details view of your account.
3. Switch to "Security credentials tabs".
4. Click on "Create access key" button.
5. Remember both keys because secret key will not be able to get the secret key from AWS system.
