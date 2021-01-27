# db_access
library to access IoT database, with devices and measurements.
Library allows adding, managing and retrieving data from database with convenient functions.


### Setup
Create virtual environment and install requirements.txt

### Configure db_access
Library can be configured with following system environments:
* **IOT_AWS_REGION** region, where are DynamoDB tables 
* **DATABASE_PREFIX** prefix added to all DynamoDB tables
* **DATABASE_HOST** you can setup it to localhost:port to use Dynalite instead of AWS DynamoDB
* **DEBUG** add "_dev" suffix for all DynamoDB tables

### AWS account configuration
Type in the terminal:
``` bash
aws configure
```
and enter the following configuration when prompted by aws cli:
```bash
AWS Access Key ID [None]: yyyy
AWS Secret Access Key [None]: xxxx
Default region name [None]: eu-west-2
Default output format [None]:
```


