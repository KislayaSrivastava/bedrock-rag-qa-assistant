# Changelog

## [0.1.0] - 2026-08-08

### Added
- Initial RAG pipeline: chunking, Bedrock Titan embeddings, ChromaDB vector store, Bedrock Claude generation
- FastAPI app with `/query` and `/health` endpoints
- Lambda handler (Mangum) for serverless deployment
- Terraform IaC: Lambda + API Gateway HTTP API + scoped IAM role
- Streamlit demo UI
- Unit tests with mocked Bedrock calls (no AWS credentials required for CI)
- GitHub Actions CI (lint + test)
- Sample document set for out-of-the-box ingestion
