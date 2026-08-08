# Lambda deployment packages over 50MB can't be uploaded directly -- they
# must go through S3 first. This bucket exists purely to stage the zip;
# force_destroy so `terraform destroy` doesn't get stuck on a non-empty bucket.
resource "aws_s3_bucket" "lambda_deploy" {
  bucket        = "${var.function_name}-deploy-${data.aws_caller_identity.current.account_id}"
  force_destroy = true
}

resource "aws_s3_object" "lambda_zip" {
  bucket = aws_s3_bucket.lambda_deploy.id
  key    = "lambda_package.zip"
  source = var.lambda_zip_path
  etag   = filemd5(var.lambda_zip_path)
}
