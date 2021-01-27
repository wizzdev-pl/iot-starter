# Parameters for Web Visualization module

# Configuration of cloudfront instance
variable "cloudfront_web_visualization" {
  type = object({
    cname = string
    api_id = string
    api_arn = string
    api_url = string
  })
}

# Configuration of S3 bucket for visualization
variable "s3_web_visualization" {
  type = object({
    bucket_name = string
  })
}

# Some AWS tags, which are taken from .tfvar file
variable "tags" {
  type = map
  default = {}
}

variable "mode" {
  type = string
}
