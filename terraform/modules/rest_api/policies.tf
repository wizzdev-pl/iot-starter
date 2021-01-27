# Define policies for specified resources
# Create 'lambda_standard_policy_document' for REST API

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

  /* Iot things */
  statement {
    actions = [
      "iot:*",
    ]
    resources = [
      "*"
    ]
  }

  /* Putting and reading logs */
  statement {
    actions = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:DescribeLogStreams"
    ]
    resources = [
      "arn:aws:logs:*:*:*"
    ]
  }

}
