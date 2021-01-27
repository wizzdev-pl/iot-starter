# Lambdas - Collect Measurement
# It takes care of architecture for collect measurements lambda
# Implemented tasks:
# - create lambda and lambda policy
# - deploy zip package to lambda
# - add cloudwatch event, which trigger lambda every X minutes, where X is defined in vars.tf file

resource "aws_lambda_function" "health_check_lambda" {
  function_name = local.lambda_health_check_name
  handler = var.lambda_health_check.function_handler
  timeout = var.lambda_health_check.function_timeout_in_seconds

  runtime = "python3.6"
  memory_size = 128

  role = aws_iam_role.health_check_iam_role.arn
  filename = data.archive_file.health_check_lambda_zip.output_path
  source_code_hash = data.archive_file.health_check_lambda_zip.output_base64sha256

  tags = var.tags
  environment {
    variables = {
      DATABASE_PREFIX = "${var.mode}_db"
      SENTRY = var.health_check_sentry_dsn
      IOT_AWS_REGION = var.region
      MODE = var.mode
    }
  }
}

resource "aws_iam_role" "health_check_iam_role" {
  name = local.lambda_health_check_name

  description = "IAM role for 'collecting measurements'"
  assume_role_policy = data.aws_iam_policy_document.lambda_standard_role_policy_document.json

  tags = var.tags
}

resource "aws_iam_role_policy_attachment" "health_check_join_policy" {
  policy_arn = aws_iam_policy.lambda_standard_policy.arn

  role = aws_iam_role.health_check_iam_role.name
}

resource "aws_cloudwatch_event_rule" "health_check_cloudwatch_event_rule" {
  name = local.lambda_health_check_name
  description = "Cron job for ${local.lambda_health_check_name}"
  schedule_expression = "rate(${var.lambda_health_check.time_between_runs_in_minutes} minutes)"

  tags = var.tags
}

resource "aws_cloudwatch_event_target" "health_check_assign_rule" {
  target_id = "lambda"
  rule = aws_cloudwatch_event_rule.health_check_cloudwatch_event_rule.name
  arn = aws_lambda_function.health_check_lambda.arn
}

resource "aws_lambda_permission" "allow_cloudwatch_to_call_check_foo" {
  statement_id = "AllowExecutionFromCloudWatch"
  action = "lambda:InvokeFunction"
  principal = "events.amazonaws.com"
  function_name = aws_lambda_function.health_check_lambda.function_name
  source_arn = aws_cloudwatch_event_rule.health_check_cloudwatch_event_rule.arn
}

data "archive_file" "health_check_lambda_zip" {
  depends_on = [
    null_resource.health_check_lambda_trigger
  ]
  type = "zip"
  source_dir = "./.tmp/lambda_health_check"
  output_path = "./.tmp/${var.lambda_health_check.function_name}.zip"
}

resource "null_resource" "health_check_lambda_trigger" {
  triggers = {
    timestamp = timestamp()
  }
  provisioner "local-exec" {
    command = "echo 1"
  }
}
// Deprecation: build with build_all.py script
//resource "null_resource" "health_check_prepare_lambda_package" {
//  provisioner "local-exec" {
//    working_dir = "./scripts"
//    command = "python build_lambda.py ../../lamba_health_check ../.tmp/lambda_health_check -v INFO --include-db-access"
//  }
//  count = var.skip_build
//  triggers = {
//    always = timestamp()
//  }
//}
