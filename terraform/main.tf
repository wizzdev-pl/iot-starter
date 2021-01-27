# Main file of IoT-Project infrastructure declaration
# It takes configuration form vars.tf file, that's located in this directory
# And from provided during execution .tfvars file (see README.md for more information)


terraform {
  # the S3 backend store tfstate file on S3 bucket
  # It's the best solution if you plan to run terraform from many hosts machines.
  # See: https://www.terraform.io/docs/backends/index.html for more information
  backend "s3" {
    bucket = "test.iot.starter"
    key = "mobile-iot.wizzdev.tfstate"
    # This is different region then the one provided in .tfvar file.
    # Due to terraform specification variable cannot be passed here
    region = "eu-west-2"
  }
}

# Set up where all created services should be placed
# The whole list of regions can be found here: https://aws.amazon.com/about-aws/global-infrastructure/regional-product-services/
provider "aws" {
  region = var.region
}

# Due to the lack of consistency of naming on AWS, some names require only '-' and some require only '_'
locals {
  prefix = "${var.project}-${var.mode}"
  prefix_ = replace(local.prefix, "-", "_")
  # Create Map Object of tags, that will be added to created AWS resources
  tags = merge(var.default_tags, map("project", var.project, "owner", var.owner, "mode", var.mode))
}

### IoT Core module
module "mobile-iot-core" {
  source = "./modules/iot_core"
  prefix = local.prefix
}

### Lambdas module
module "mobile-iot-lambdas" {
  source = "./modules/lambdas"

  # General settings
  mode = var.mode
  region = var.region
  tags = local.tags

  # Lambdas configuration
  lambda_policy_name = "${local.prefix}-standard-policy"
  lambda_collect_measurements = {
    function_name = "${local.prefix}-collect-measurements"
    function_handler = "main.main"
    function_timeout_in_seconds = 60
  }
  lambda_health_check = {
    function_name = "${local.prefix}-health-check"
    function_handler = "main.main"
    function_timeout_in_seconds = 60
    time_between_runs_in_minutes = 45
  }

  # Sentry integration
  collect_measurements_sentry_dsn = var.sentry_collect_measurements
  health_check_sentry_dsn = var.sentry_health_check
}


### REST API module
module "mobile-iot-web-server" {
  source = "./modules/rest_api"

  # General settings
  region = var.region
  prefix = local.prefix

  # REST API configuration
  rest_api_python_source_directory = "../../web_server/server"
  rest_api_s3_bucket_name = "${local.prefix}-web-server-lambda"
  rest_api_lambda_handler = "app.app"
  rest_api_lambda_runtime = "python3.7"
  rest_api_lambda_environment = {
    # ESP Passwords
    ESP_HARD_PASSWORD = var.ESP_HARD_PASSWORD
    ESP_HARD_LOGIN = var.ESP_HARD_LOGIN
    # DBLib
    DEVELOPMENT = var.mode == "development"? true : false
    DATABASE_PREFIX = "${var.mode}_db"
    IOT_AWS_REGION = var.region
    # Flask API
    SECRET_KEY = "624QnZdvBsuYzscCBadfd1Dg2tXxjpeMQXy3Sk7DE0RSfX4GZNKCG0CAvbUXIYeWIe"
    # Sentry integration
    MODE = var.mode
    SENTRY = var.sentry_rest_api
    # AWS oriented settings, used for creating new things
    API_REGION_AWS = var.region
    THING_TYPE_BASE_AWS = module.mobile-iot-core.base_thing_type
    THING_POLICY_BASE_AWS = module.mobile-iot-core.base_thing_policy
  }
}


### Web visualization module
module "mobile-iot-visualization" {
  source = "./modules/web_visualization"

  # General settings
  tags = local.tags
  mode = var.mode

  # Cloudfront configuration
  cloudfront_web_visualization = {
    cname = var.mode == "production" ? "mobile-iot.wizzdev.pl" : "mobile-iot-${var.mode}.wizzdev.pl"
    api_id = module.mobile-iot-web-server.rest_api_api_id
    api_arn = module.mobile-iot-web-server.rest_api_api_arn
    api_url = module.mobile-iot-web-server.rest_api_url
  }
  # S3 configuration
  s3_web_visualization = {
    bucket_name = "${replace(local.prefix, "_", "-")}-web-visualization"
  }
}


output "thing_type_base" {
  value = module.mobile-iot-core.base_thing_type
}

output "aws_iot_endpoint" {
  value = module.mobile-iot-core.url_iot_endpoint
}

output "visualization_url" {
  value = module.mobile-iot-visualization.url_visualization
}

output "esp_login" {
  value = var.ESP_HARD_LOGIN
}

output "esp_password" {
  value = var.ESP_HARD_PASSWORD
}