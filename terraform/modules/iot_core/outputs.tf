# Save Account IoT Endpoint to tfstate file

data aws_iot_endpoint "wizzdev_iot_endpoint" {}

output "url_iot_endpoint" {
   value = data.aws_iot_endpoint.wizzdev_iot_endpoint
 }

output "base_thing_type" {
  value = aws_iot_thing_type.iot_thing_type_base.name
}

output "base_thing_policy" {
  value = aws_iot_policy.iot_core_policy.name
}