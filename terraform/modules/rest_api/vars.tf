# Parameters for REST API module

# S3 bucket name for REST API lambda code
variable "rest_api_s3_bucket_name" {
  type = string
}

# Source dir relative path
variable "rest_api_python_source_directory" {
  type = string
}

# Handler to flask application
variable "rest_api_lambda_handler" {
  type = string
}

# Which version of python lambda should use
variable "rest_api_lambda_runtime" {
  type = string
}

# Prefix will be attached to names and descriptions
variable "prefix" {
  type = string
  default = ""
}

variable "region" {
  type = string
}

# Set up system environment variables for lambda
variable "rest_api_lambda_environment" {
  type = map(string)
  default = {
    VERSION = 1
  }
}

# Maximum time of lambda run
variable "rest_api_lambda_timeout" {
  type = string
  default = "35"
}

