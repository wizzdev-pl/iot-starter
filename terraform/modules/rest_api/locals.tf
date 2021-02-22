# Create REST API specific names
# Due to the lack of consistency of naming on AWS, some names require only '-' and some require only '_'

locals {
  name = replace("${var.prefix}-${basename(var.rest_api_python_source_directory)}", "_", "-")
  s3_bucket_name = replace(var.rest_api_s3_bucket_name, "_", "-")
}
