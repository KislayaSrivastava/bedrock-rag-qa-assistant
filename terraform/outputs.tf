output "api_endpoint" {
  description = "Invoke URL for the deployed RAG API"
  value       = aws_apigatewayv2_stage.default_stage.invoke_url
}

output "lambda_function_name" {
  value = aws_lambda_function.rag_api.function_name
}
