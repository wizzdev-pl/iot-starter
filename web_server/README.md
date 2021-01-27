# Web Server
`web_server` is a flask based application, hosting static html sites and dynamic API to request measurements data.
It uses library `db_access` to access the data from dynamodb.
Application is supposed to be hosted on AWS serveless, with access via www, without any logging.
Dedicated site allows to see list of devices, graphs and download the data as csv.

### Development
For local development, `web_server` can be hosted locally - just run `./src/main.py` file.
Make sure that both `db_access` and `web_server` directories are in path and `requirementst.txt` are installed.

### Configuration
Server can be configured with system environments:
* **PAGE_SIZE** (TBD)
* **CORS** Turn on/off CORS. Cors is enabled by default. 
* **NO_ROBOTS** Disable search engine spiders. Enabled by default.

And some more from ***db_access*** library:
* **IOT_AWS_REGION** region, where are DynamoDB tables 
* **DATABASE_PREFIX** prefix added to all DynamoDB tables
* **DATABASE_HOST** you can setup it to localhost:port to use Dynalite instead of AWS DynamoDB
* **DEBUG** add "_dev" suffix for all DynamoDB tables

# Hosting with serverless
```
sudo apt install npm
```
Pack `web_server` and `db_access` directories (both need to be in path) and install requirements.
TODO - how to host it


