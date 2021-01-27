# Parameters for Lambdas module

# Will be taken from environments/file.tfvars
variable region {
  type = string
}

# Will be taken from environments/file.tfvars
variable "mode" {
  type = string
}

# Will be constructed basing on environments/file.tfvars
variable "tags" {
  type = map
  default = {}
}


# Default lambda oriented settings
variable lambda_policy_name {
  type = string
}

# Configuration of lambda_collect_measurements
variable "lambda_collect_measurements" {
  type = object({
    function_name = string,
    function_handler = string
    function_timeout_in_seconds = number
  })
}

# Configuration of lambda_health_check
variable "lambda_health_check" {
  type = object({
    function_name = string,
    function_handler = string
    function_timeout_in_seconds = number
    time_between_runs_in_minutes = number
  })
}


# Configuration of sentry integration
# It's optional feature, that doesn't needs to be provided
variable "collect_measurements_sentry_dsn" {
  type = string
  default = ""
}

# Configuration of sentry integration
# It's optional feature, that doesn't needs to be provided
variable "health_check_sentry_dsn" {
  type = string
  default = ""
}