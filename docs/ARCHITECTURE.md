# Architecture

## Overview

This project implements a standard two-phase RAG architecture: an **offline ingestion phase** that builds a searchable knowledge base, and an **online query phase** that answers questions grounded in that knowledge base.

## 1. Ingestion Flow

```
data/*.md, *.txt
      |
      v
 chunk_text()            src/ingest.py -- recursive character-based
      |                  chunking with configurable size/overlap
      v
 Bedrock Titan Embed     one embedding call per chunk (batched)
      |
      v
 ChromaDB.add()          persisted to disk under CHROMA_PERSIST_DIR
```

Design choices:
- **Chunking** uses a simple recursive splitter (paragraph -> sentence -> fixed-width fallback) rather than a heavy framework dependency, to keep the ingestion path easy to read and modify.
- **ChromaDB** was chosen over a managed vector store (OpenSearch Serverless, Pinecone) for the reference implementation because it runs locally with zero additional AWS spend -- swapping it for a managed store only touches `src/retriever.py` and `src/ingest.py`.

## 2. Query Flow

```
question
   |
   v
Bedrock Titan Embed  ->  ChromaDB.query() (top-k similarity search)
                              |
                              v
                         retrieved chunks + metadata
                              |
                              v
                    prompt assembly (src/generator.py)
                              |
                              v
                     Bedrock Claude (generation)
                              |
                              v
                    { answer, sources, latency_ms }
```

The prompt template instructs the model to answer **only** from the retrieved context and to say so explicitly when the context doesn't contain the answer, rather than falling back to parametric knowledge -- this keeps answers grounded and auditable via the returned `sources`.

## 3. Deployment Shapes

The same FastAPI app (`src/api.py`) is used in both modes:

| Mode | Entrypoint | Notes |
|---|---|---|
| Local | `uvicorn src.api:app` | For development and the ingestion step |
| Serverless | `lambda/handler.py` (Mangum-wrapped) behind API Gateway | Provisioned via `terraform/` |

**Note on the serverless path:** ChromaDB in Lambda needs a persistent volume (EFS) or a swap to a managed vector store for production use, since Lambda's local filesystem doesn't persist across invocations. The Terraform in this repo provisions the Lambda + API Gateway + IAM layer; wiring up EFS or a managed vector store is left as the next milestone (see README roadmap) rather than adding that complexity to a 24-hour reference build.

## 4. IAM / Security

The Lambda execution role is scoped to:
- `bedrock:InvokeModel` on the specific embedding and generation model ARNs (not `*`)
- CloudWatch Logs write access for the function's own log group

No other AWS permissions are granted.

## 5. Why Bedrock over a direct model API

Using Bedrock (vs. calling a model provider's API directly) keeps model invocation inside the AWS account boundary -- same IAM, same VPC options, same CloudWatch/X-Ray observability surface as the rest of an AWS-native platform -- which matches how this pattern would actually be deployed inside a larger AWS-resident system.
