# API Reference

Base URL: `http://localhost:8000` (local) or the API Gateway invoke URL (deployed)

## `POST /query`

Ask a question against the ingested knowledge base.

**Request body**

```json
{
  "question": "What is the AWS Well-Architected Framework?",
  "top_k": 4
}
```

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| `question` | string | yes | -- | The question to answer |
| `top_k` | integer | no | 4 | Number of chunks to retrieve before generation |

**Response `200 OK`**

```json
{
  "answer": "The AWS Well-Architected Framework is ...",
  "sources": [
    {
      "chunk_id": "aws-well-architected-summary.md::chunk-2",
      "source_file": "aws-well-architected-summary.md",
      "score": 0.83,
      "text_preview": "The framework is organized around six pillars: operational excellence, security..."
    }
  ],
  "latency_ms": 842
}
```

**Response `200 OK` -- no relevant context found**

```json
{
  "answer": "I don't have enough information in the provided context to answer that.",
  "sources": [],
  "latency_ms": 210
}
```

**Error responses**

| Status | Cause |
|---|---|
| `422` | Missing/invalid `question` field |
| `500` | Bedrock invocation failure (see `detail` in response body) |

## `GET /health`

Liveness/readiness check.

**Response `200 OK`**

```json
{
  "status": "ok",
  "vector_store_ready": true,
  "chunk_count": 18
}
```
