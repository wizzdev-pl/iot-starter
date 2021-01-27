# Iot Core module
# It takes care of establish connection between IoT devices and AWS Cloud
# Implemented tasks:
# - two thing types: base and test
# - iot things policy

resource "aws_iot_thing_type" "iot_thing_type_base" {
  name = "${var.prefix}_tf"
}

resource "aws_iot_thing_type" "iot_thing_type_test" {
  name = "${var.prefix}_test"
}

resource "aws_iot_policy" "iot_core_policy" {
  name = "${var.prefix}_iot_core_connect_and_publish_to_topic"
  policy = data.aws_iam_policy_document.iot_core_policy_document.json
}