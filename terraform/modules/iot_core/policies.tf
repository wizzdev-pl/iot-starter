# Thing policy allow to publish, subscribe, connect and receive

data "aws_iam_policy_document" "iot_core_policy_document" {
  statement {
    actions = [
      "iot:Publish",
      "iot:Subscribe",
      "iot:Connect",
      "iot:Receive"
    ]
    resources = [
      "*"
    ]
  }
}
