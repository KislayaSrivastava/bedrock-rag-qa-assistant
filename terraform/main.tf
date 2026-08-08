terraform {
  required_version = ">= 1.5"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

resource "aws_lambda_function" "rag_api" {
  function_name = var.function_name
  role          = aws_iam_role.lambda_exec.arn
  handler       = "lambda.handler.handler"
  runtime       = "python3.12"
  timeout       = 30
  memory_size   = 512

  s3_bucket        = aws_s3_bucket.lambda_deploy.id
  s3_key           = aws_s3_object.lambda_zip.key
  source_code_hash = filebase64sha256(var.lambda_zip_path)

  environment {
    variables = {
      AWS_REGION_OVERRIDE       = var.aws_region
      BEDROCK_EMBED_MODEL_ID    = var.embed_model_id
      BEDROCK_GEN_MODEL_ID      = var.gen_model_id
      CHROMA_PERSIST_DIR        = "/tmp/chroma_db"
      # Its gRPC-based exporter package is deliberately pruned from the
      # deployment zip to fit Lambda's size limit -- disable the feature
      # explicitly rather than relying on it silently failing to import.
      CHROMA_ANONYMIZED_TELEMETRY = "false"
      ANONYMIZED_TELEMETRY        = "false"
    }
  }
}

resource "aws_apigatewayv2_api" "http_api" {
  name          = "${var.function_name}-api"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_integration" "lambda_integration" {
  api_id                 = aws_apigatewayv2_api.http_api.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.rag_api.invoke_arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "default_route" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "$default"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_integration.id}"
}

resource "aws_apigatewayv2_stage" "default_stage" {
  api_id      = aws_apigatewayv2_api.http_api.id
  name        = "$default"
  auto_deploy = true
}

resource "aws_lambda_permission" "apigw_invoke" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.rag_api.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.http_api.execution_arn}/*/*"
}

resource "aws_cloudwatch_log_group" "lambda_logs" {
  name              = "/aws/lambda/${var.function_name}"
  retention_in_days = 14
}
