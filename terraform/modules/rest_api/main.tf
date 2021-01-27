# REST API module
# It takes care of setting up REST API, which is responsible for:
# - providing data to visualization
# - communicate with ESP32 to create thing in AWS
# Implemented tasks:
# - create S3 bucket for lambda code
# - configure API gateway
# - create lambda and attach policy

resource "aws_s3_bucket" "rest_api_s3_bucket" {
  bucket = local.s3_bucket_name
  force_destroy = true
  acl = "private"
}

resource "aws_s3_bucket_object" "rest_api_upload_archived_lambda" {
  bucket = aws_s3_bucket.rest_api_s3_bucket.bucket
  key = data.archive_file.rest_api_archive_lambda.output_base64sha256
  source = data.archive_file.rest_api_archive_lambda.output_path

  # Terraform AWS Provider bug, https://github.com/terraform-providers/terraform-provider-aws/issues/12387
  # etag = "${filemd5(data.archive_file.rest_api_archive_lambda.output_path)}"

  depends_on = [
    aws_s3_bucket.rest_api_s3_bucket,
    data.archive_file.rest_api_archive_lambda
  ]
}

resource "aws_api_gateway_rest_api" "rest_api_gateway_rest_api" {
  name = local.name
  description = "${local.name} - Rest API, from ${data.archive_file.rest_api_archive_lambda.source_dir}"
}

resource "aws_api_gateway_resource" "rest_api_proxy_resource" {
  rest_api_id = aws_api_gateway_rest_api.rest_api_gateway_rest_api.id
  parent_id = aws_api_gateway_rest_api.rest_api_gateway_rest_api.root_resource_id
  path_part = "{proxy+}"
}

resource "aws_api_gateway_method" "rest_api_proxy_method" {
  rest_api_id = aws_api_gateway_rest_api.rest_api_gateway_rest_api.id
  resource_id = aws_api_gateway_resource.rest_api_proxy_resource.id
  http_method = "ANY"
  authorization = "NONE"
  authorizer_id = ""
}

resource "aws_api_gateway_integration" "rest_api_proxy_lambda" {
  rest_api_id = aws_api_gateway_rest_api.rest_api_gateway_rest_api.id
  resource_id = aws_api_gateway_method.rest_api_proxy_method.resource_id
  http_method = aws_api_gateway_method.rest_api_proxy_method.http_method

  integration_http_method = "POST"
  type = "AWS_PROXY"
  uri = aws_lambda_function.rest_api_lambda_resource.invoke_arn
}

resource "aws_api_gateway_method" "rest_api_proxy_method_root" {
  rest_api_id = aws_api_gateway_rest_api.rest_api_gateway_rest_api.id
  resource_id = aws_api_gateway_rest_api.rest_api_gateway_rest_api.root_resource_id
  http_method = "ANY"
  authorization = "NONE"
  authorizer_id = ""
}

resource "aws_api_gateway_integration" "rest_api_proxy_lambda_root" {
  rest_api_id = aws_api_gateway_rest_api.rest_api_gateway_rest_api.id
  resource_id = aws_api_gateway_method.rest_api_proxy_method_root.resource_id
  http_method = aws_api_gateway_method.rest_api_proxy_method_root.http_method

  integration_http_method = "POST"
  type = "AWS_PROXY"
  uri = aws_lambda_function.rest_api_lambda_resource.invoke_arn
}

resource "aws_api_gateway_deployment" "rest_api_deployment_api" {
  depends_on = [
    aws_api_gateway_integration.rest_api_proxy_lambda,
    aws_api_gateway_integration.rest_api_proxy_lambda_root
  ]

  rest_api_id = aws_api_gateway_rest_api.rest_api_gateway_rest_api.id
  stage_name = "API"
  description = "Created from Terraform"
}

resource "aws_lambda_permission" "rest_api_lambda_api_permissions" {
  statement_id = "AllowAPIGatewayInvoke"
  action = "lambda:InvokeFunction"
  function_name = aws_lambda_function.rest_api_lambda_resource.arn
  principal = "apigateway.amazonaws.com"

  # The /*/* portion grants access from any method on any resource
  # within the API Gateway "REST API".
  source_arn = "${aws_api_gateway_rest_api.rest_api_gateway_rest_api.execution_arn}/*/*"
}

resource "aws_lambda_function" "rest_api_lambda_resource" {
  function_name = local.name
  s3_bucket = aws_s3_bucket.rest_api_s3_bucket.bucket
  s3_key = aws_s3_bucket_object.rest_api_upload_archived_lambda.key
  handler = var.rest_api_lambda_handler
  runtime = var.rest_api_lambda_runtime
  timeout = var.rest_api_lambda_timeout
  role = aws_iam_role.rest_api_lambda_role.arn

  environment {
    variables = var.rest_api_lambda_environment
  }
}

resource "aws_iam_role" "rest_api_lambda_role" {
  name = "${var.rest_api_s3_bucket_name}-lambda"
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy" "rest_api_lambda_role_policy" {
  name = "${local.name}-lambda-logs"
  role = aws_iam_role.rest_api_lambda_role.id
  policy = data.aws_iam_policy_document.lambda_standard_policy_document.json
}

# Trigger that will be run every terraform execute, this ensure that terraform always builds fresh zip package with code
resource "null_resource" "trigger" {
  triggers = {
    timestamp = timestamp()
  }
  provisioner "local-exec" {
    command = "echo 1"
  }
}

data "archive_file" "rest_api_archive_lambda" {
  depends_on = [
    null_resource.trigger
  ]
  type = "zip"
  source_dir = ".tmp/rest_api"
  output_path = ".tmp/rest_api.zip"
}

// Deprecation: build with build_all.py script
//resource "null_resource" "rest_api_pack_lambda" {
//  count = var.skip_build
//  triggers = {
//    timestamp = timestamp()
//  }
//  provisioner "local-exec" {
//    working_dir = "./scripts"
//    command = "python build_lambda.py ${var.rest_api_python_source_directory} ../.tmp/rest_api -v DEBUG --include-db-access"
//  }
//}
