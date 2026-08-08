# Bedrock RAG QA Assistant

Retrieval-Augmented Generation (RAG) Q&A service built on **Amazon Bedrock** — Titan Embeddings for retrieval, Claude for generation, ChromaDB for vector storage, with a serverless deployment path via Lambda + API Gateway (Terraform).

Ask a question, get an answer grounded in your own documents, with sources cited — running locally in minutes or deployed serverless on AWS.

---

## Why this exists

A hands-on reference implementation of a production-shaped RAG pipeline on AWS Bedrock — built to go deeper than a notebook demo: a real API, real IaC, real tests, and a real deployment path.

## Architecture

```mermaid
flowchart LR
    subgraph Ingestion["Ingestion (offline)"]
        A[Documents<br/>data/] --> B[Chunker]
        B --> C[Titan Embeddings<br/>Bedrock]
        C --> D[(ChromaDB<br/>vector store)]
    end

    subgraph Query["Query (online)"]
        E[Question] --> F[Titan Embeddings<br/>Bedrock]
        F --> G[Similarity Search]
        D --> G
        G --> H[Top-K Chunks]
        H --> I[Prompt Assembly]
        E --> I
        I --> J[Claude<br/>Bedrock]
        J --> K[Answer + Sources]
    end
```

**Two deployment shapes, same code:**
- **Local / API** — FastAPI app (`src/api.py`), run with `uvicorn`
- **Serverless** — same FastAPI app wrapped for Lambda (`lambda/handler.py` via Mangum), fronted by API Gateway, provisioned with Terraform (`terraform/`)

## Tech Stack

| Layer | Choice |
|---|---|
| Embeddings | Amazon Bedrock — Titan Embed Text v2 |
| Generation | Amazon Bedrock — Claude (model configurable) |
| Vector store | ChromaDB (local, persisted) |
| API | FastAPI + Uvicorn |
| Serverless runtime | AWS Lambda (via Mangum) + API Gateway (HTTP API) |
| IaC | Terraform |
| Demo UI | Streamlit |
| Tests | pytest, mocked Bedrock calls (no AWS credentials needed to run CI) |

## What this demonstrates

- Amazon Bedrock (embeddings + generation), RAG pipeline design, prompt engineering
- Infrastructure-as-Code (Terraform) for a serverless AWS deployment
- API design (FastAPI), automated testing, CI (GitHub Actions)

## Project Structure

```
bedrock-rag-qa-assistant/
├── src/                  # Core RAG pipeline + API
│   ├── config.py
│   ├── ingest.py         # Chunk + embed + store documents
│   ├── retriever.py      # Embed query + similarity search
│   ├── generator.py      # Bedrock Claude prompt + generation
│   ├── rag_pipeline.py   # Orchestrates retriever + generator
│   └── api.py            # FastAPI app (/query, /health)
├── lambda/handler.py     # Lambda entrypoint (Mangum adapter)
├── terraform/            # Lambda + API Gateway + IAM (IaC)
├── streamlit_app.py      # Demo UI
├── data/sample_docs/     # Sample documents to ingest
├── tests/                # Unit tests (mocked Bedrock)
└── docs/                 # Architecture, quickstart, API reference
```

## Quickstart

See [docs/QUICKSTART.md](docs/QUICKSTART.md) for full setup. Short version:

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # fill in your AWS region / model IDs

python -m src.ingest          # embeds data/sample_docs into ChromaDB
uvicorn src.api:app --reload  # starts the API on :8000

curl -X POST localhost:8000/query -H "Content-Type: application/json" \
  -d '{"question": "What is the AWS Well-Architected Framework?"}'
```

## Deploying to AWS

```bash
cd terraform
terraform init
terraform apply
```

Provisions a Lambda function (Bedrock `InvokeModel` permissions scoped via IAM), an API Gateway HTTP API in front of it, and CloudWatch logging. See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for details.

## Documentation

- [Architecture](docs/ARCHITECTURE.md) — ingestion/query flow, deployment shapes, design decisions
- [Quickstart](docs/QUICKSTART.md) — full local setup walkthrough
- [API Reference](docs/API.md) — endpoint spec

## Roadmap

- [ ] Swap ChromaDB for OpenSearch Serverless for a fully-managed vector store option
- [ ] Add streaming responses (Bedrock `invoke_model_with_response_stream`)
- [ ] Add re-ranking step before generation
- [ ] Multi-format ingestion (PDF, DOCX) beyond .txt/.md

## License

MIT — see [LICENSE](LICENSE)
