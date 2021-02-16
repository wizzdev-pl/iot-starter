# Create lambdas specific names
# Due to the lack of consistency of naming on AWS, some names require only '-' and some require only '_'

locals {
  lambda_collect_measurements_name = replace(var.lambda_collect_measurements.function_name, "_", "-")
  lambda_collect_measurements_name_ = replace(var.lambda_collect_measurements.function_name, "-", "_")
  lambda_health_check_name = replace(var.lambda_health_check.function_name, "_", "-")
  lambda_health_check_name_ = replace(var.lambda_health_check.function_name, "-", "_")
}
