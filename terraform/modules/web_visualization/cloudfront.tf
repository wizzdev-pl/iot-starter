# Web Visualization - Cloudfront
# It creates cloudfront instance that enables access to Website and API from outside
# Implemented task:
# - cloudfront instance with Visualization and REST API origins
# - certificate for cloudfront instance

data aws_arn "web_server_api_gateway_arn" {
  arn = var.cloudfront_web_visualization.api_arn
}

# Save origins names in locals namespace, because they are accessed in many places
locals {
  visualization_origin = "Visualization"
  api_dev_origin = "APIDEV"
  api_api_origin = "APIAPI"
}

# Create certificate for Cloudfront instance
resource "aws_acm_certificate" "web_visualization_cname_certificate" {
  domain_name = var.cloudfront_web_visualization.cname
  validation_method = "DNS"

  lifecycle {
    create_before_destroy = true
  }

  tags = var.tags
}

resource "aws_cloudfront_distribution" "visualization_cloudfront" {
  default_root_object = "index.html"
  enabled = "true"
  http_version = "http2"
  is_ipv6_enabled = "true"

  custom_error_response {
    error_caching_min_ttl = "0"
    error_code = "403"
    response_code = "200"
    response_page_path = "/index.html"
  }

  custom_error_response {
    error_caching_min_ttl = "0"
    error_code = "404"
    response_code = "200"
    response_page_path = "/index.html"
  }

  default_cache_behavior {
    allowed_methods = [
      "GET",
      "HEAD"
    ]
    cached_methods = [
      "HEAD",
      "GET"
    ]
    compress = "false"
    default_ttl = "86400"

    forwarded_values {
      cookies {
        forward = "none"
      }

      query_string = "false"
    }

    max_ttl = "31536000"
    min_ttl = "0"
    smooth_streaming = "false"
    target_origin_id = local.visualization_origin
    viewer_protocol_policy = "redirect-to-https"
  }

    ordered_cache_behavior {
      allowed_methods = [
        "DELETE",
        "PUT",
        "OPTIONS",
        "GET",
        "POST",
        "HEAD",
        "PATCH"
      ]
      cached_methods = [
        "GET",
        "HEAD"
      ]
      compress = "true"
      default_ttl = "300"

      forwarded_values {
        cookies {
          forward = "none"
        }

        query_string = "true"
      }

      max_ttl = "300"
      min_ttl = "0"
      path_pattern = "/api/*"
      smooth_streaming = "false"
      target_origin_id = local.api_api_origin
      viewer_protocol_policy = "redirect-to-https"
    }

    ordered_cache_behavior {
      allowed_methods = [
        "DELETE",
        "GET",
        "HEAD",
        "PATCH",
        "POST",
        "OPTIONS",
        "PUT"
      ]
      cached_methods = [
        "GET",
        "HEAD"
      ]
      compress = "true"
      default_ttl = "86400"

      forwarded_values {
        cookies {
          forward = "none"
        }

        query_string = "false"
      }

      max_ttl = "31536000"
      min_ttl = "0"
      path_pattern = "/dev/*"
      smooth_streaming = "false"
      target_origin_id = local.api_api_origin
      viewer_protocol_policy = "redirect-to-https"
    }

    /* Api /api Origin */
    origin {
      custom_origin_config {
        http_port = "80"
        https_port = "443"
        origin_keepalive_timeout = "5"
        origin_protocol_policy = "https-only"
        origin_read_timeout = "30"
        origin_ssl_protocols = [
          "TLSv1.2"
        ]
      }

      domain_name = var.cloudfront_web_visualization.api_url
      origin_id = local.api_api_origin
      origin_path = "/API"
    }

  /* Visualization Origin */
  origin {
    custom_origin_config {
      http_port = "80"
      https_port = "443"
      origin_keepalive_timeout = "5"
      origin_protocol_policy = "http-only"
      origin_read_timeout = "30"
      origin_ssl_protocols = [
        "TLSv1.2"
      ]
    }

    domain_name = aws_s3_bucket.web_visualization_s3_bucket.website_endpoint
    origin_id = local.visualization_origin
  }

  price_class = "PriceClass_All"

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  retain_on_delete = "false"

  viewer_certificate {
    cloudfront_default_certificate = true
  }

}