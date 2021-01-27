# Web Visualization - S3 bucket
# It creates S3 bucket with provided name and attach to it policy that allow public read access

resource "aws_s3_bucket" "web_visualization_s3_bucket" {
  bucket = var.s3_web_visualization.bucket_name

  acl = "public-read"
  force_destroy = true

  website {
    index_document = "index.html"
    error_document = "index.html"
  }

  tags = var.tags
}

# Policy that allows public read only access to S3 bucket
resource "aws_s3_bucket_policy" "web_visualization_s3_bucket_policy" {
  bucket = aws_s3_bucket.web_visualization_s3_bucket.id
  policy = <<POLICY
{
  "Version": "2008-10-17",
  "Statement": [{
    "Sid": "AllowPublicRead",
    "Effect": "Allow",
    "Principal": {
      "AWS": "*"
    },
    "Action": [ "s3:GetObject" ],
    "Resource": [ "${aws_s3_bucket.web_visualization_s3_bucket.arn}/*"]
  }]
}
POLICY
}

# Run build script that uploads visualization package to S3 bucket
resource "null_resource" "web_visualization_prepare_s3_package" {
  triggers = {
    timestamp = timestamp()  # Run always
  }

  depends_on = [
    aws_s3_bucket.web_visualization_s3_bucket
  ]
  provisioner "local-exec" {
    working_dir = "./scripts"
    command = "python3 upload_frontend.py ${var.s3_web_visualization.bucket_name} ../.tmp/build_visualization -v INFO"
  }
}