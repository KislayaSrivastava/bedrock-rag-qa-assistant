variable "aws_region" {
  description = "AWS region to deploy into"
  type        = string
  default     = "us-east-1"
}

variable "function_name" {
  description = "Name for the Lambda function"
  type        = string
  default     = "bedrock-rag-qa-assistant"
}

variable "embed_model_id" {
  description = "Bedrock model ID used for embeddings"
  type        = string
  default     = "amazon.titan-embed-text-v2:0"
}

variable "gen_model_id" {
  description = "Bedrock model ID used for generation"
  type        = string
  default     = "anthropic.claude-3-5-sonnet-20241022-v2:0"
}

variable "lambda_zip_path" {
  description = "Path to the built Lambda deployment package (see scripts/build_lambda_zip.sh)"
  type        = string
  default     = "../build/lambda_package.zip"
}
