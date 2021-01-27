output "url_visualization" {
  value = aws_cloudfront_distribution.visualization_cloudfront.domain_name
}