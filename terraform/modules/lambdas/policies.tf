# Define policies for specified resources
# Create 'lambda_standard_policy' and 'lambda_iot_core_access_policy'

data "aws_iam_policy_document" "lambda_iot_core_access_policy_document" {
  statement {
    actions = [
      "iot:GetThingShadow",
    ]
    resources = [
      "*"
    ]
  }
}
data "aws_iam_policy_document" "lambda_standard_policy_document" {

  /* Dynamodb Access */
  statement {
    actions = [
      "dynamodb:PutItem",
      "dynamodb:DescribeTable",
      "dynamodb:CreateTable",
      "dynamodb:GetItem",
      "dynamodb:Scan",
      "dynamodb:Query",
      "dynamodb:UpdateItem",
      "dynamodb:BatchWriteItem",
      "dynamodb:BatchGetItem",
    ]
    resources = [
      "*"
    ]
  }

  /* Sending Mails, SES */
  # TODO: remove it in starter
  statement {
    actions = [
      "ses:SendEmail",
      "ses:SendRawEmail"
    ]
    resources = [
      "*"
    ]
  }

  /* Putting and reading logs */
  statement {
    actions = [
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]
    resources = [
      "arn:aws:logs:*:*:*"
    ]
  }
}
data "aws_iam_policy_document" "lambda_standard_role_policy_document" {
  statement {
    actions = [
      "sts:AssumeRole"
    ]
    principals {
      type = "Service"
      identifiers = [
        "lambda.amazonaws.com"
      ]
    }
  }
}

resource "aws_iam_policy" "lambda_standard_policy" {
  name = var.lambda_policy_name
  policy = data.aws_iam_policy_document.lambda_standard_policy_document.json
}

resource "aws_iam_policy" "lambda_iot_core_access_policy" {
  name = "${var.lambda_policy_name}_for_iot_core"
  policy = data.aws_iam_policy_document.lambda_iot_core_access_policy_document.json
}
