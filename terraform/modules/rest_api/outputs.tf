# Save REST API parameters
# They will be saved in tfstate file and always are used by Web Visualization module

output "rest_api_api_id" {
  value = aws_api_gateway_rest_api.rest_api_gateway_rest_api.id
}

output "rest_api_api_arn" {
  value = aws_api_gateway_rest_api.rest_api_gateway_rest_api.arn
}

output "rest_api_url" {
  value = "${aws_api_gateway_rest_api.rest_api_gateway_rest_api.id}.execute-api.${var.region}.amazonaws.com"
}

output "rest_api_role_id" {
  value = aws_iam_role.rest_api_lambda_role.id
}