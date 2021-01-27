# Lambdas - Collect Measurement
# It takes care of architecture for collect measurements lambda
# Implemented tasks:
# - create lambda and lambda policy
# - deploy zip package to lambda
# - trigger lambda with new reads from Iot device

resource "aws_lambda_function" "collect_measurements_lambda" {
  function_name = local.lambda_collect_measurements_name
  handler = var.lambda_collect_measurements.function_handler
  timeout = var.lambda_collect_measurements.function_timeout_in_seconds

  runtime = "python3.6"
  memory_size = 128

  role = aws_iam_role.collect_measurements_iam_role.arn
  filename = data.archive_file.collect_measurements_lambda_zip.output_path
  source_code_hash = data.archive_file.collect_measurements_lambda_zip.output_base64sha256

  tags = var.tags
  environment {
    variables = {
      DATABASE_PREFIX = "${var.mode}_db"
      SENTRY = var.collect_measurements_sentry_dsn
      IOT_AWS_REGION = var.region
      MODE = var.mode
    }
  }
}

resource "aws_iot_topic_rule" "collect_measurements_iot_core_topic" {
  name = local.lambda_collect_measurements_name_

  sql = "SELECT * FROM 'topic/data'"
  sql_version = "2015-10-08"
  enabled = true

  lambda {
    function_arn = aws_lambda_function.collect_measurements_lambda.arn
  }
}

resource "aws_iam_role" "collect_measurements_iam_role" {
  name = local.lambda_collect_measurements_name

  description = "IAM role for 'collecting measurements'"
  assume_role_policy = data.aws_iam_policy_document.lambda_standard_role_policy_document.json

  tags = var.tags
}

resource "aws_iam_role_policy_attachment" "collect_measurements_join_policy" {
  policy_arn = aws_iam_policy.lambda_standard_policy.arn

  role = aws_iam_role.collect_measurements_iam_role.name
}

resource "aws_iam_role_policy_attachment" "collect_measurements_join_policy_iot_core_access" {
  policy_arn = aws_iam_policy.lambda_iot_core_access_policy.arn

  role = aws_iam_role.collect_measurements_iam_role.name
}

resource "null_resource" "collect_measurements_lambda_trigger" {
  triggers = {
    timestamp = timestamp()
  }
  provisioner "local-exec" {
    command = "echo 1"
  }
}

data "archive_file" "collect_measurements_lambda_zip" {
  depends_on = [
    null_resource.collect_measurements_lambda_trigger
  ]
  type = "zip"
  source_dir = "./.tmp/lambda_collect_measurements"
  output_path = "./.tmp/${var.lambda_collect_measurements.function_name}.zip"
}

// Deprecation: build with build_all.py script
//resource "null_resource" "collect_measurements_prepare_lambda_package" {
//  provisioner "local-exec" {
//    working_dir = "./scripts"
//    command = "python build_lambda.py ../../lambda_collect_measurements ../.tmp/lambda_collect_measurements -v INFO --include-db-access"
//  }
//  count = var.skip_build
//  triggers = {
//    always = timestamp()
//  }
//}