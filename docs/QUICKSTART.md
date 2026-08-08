# Quickstart

## Prerequisites

- Python 3.11+
- An AWS account with **Amazon Bedrock model access enabled** for:
  - An embedding model (default: `amazon.titan-embed-text-v2:0`)
  - A generation model (default: a Claude model on Bedrock -- check the [Bedrock console -> Model access](https://console.aws.amazon.com/bedrock/) page in your region for the exact model ID currently available to your account, and set it in `.env`)
- AWS credentials configured locally (`aws configure`, or environment variables, or an SSO profile) with `bedrock:InvokeModel` permission

## 1. Clone and install

```bash
git clone https://github.com/KislayaSrivastava/bedrock-rag-qa-assistant.git
cd bedrock-rag-qa-assistant

python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

## 2. Configure

```bash
cp .env.example .env
```

Edit `.env` and set:
- `AWS_REGION` -- the region where you enabled Bedrock model access
- `BEDROCK_EMBED_MODEL_ID` -- defaults to Titan Embed Text v2
- `BEDROCK_GEN_MODEL_ID` -- set this to a Claude model ID enabled in your account/region

## 3. Ingest the sample documents

```bash
python -m src.ingest
```

This reads everything under `data/sample_docs/`, chunks it, embeds each chunk via Bedrock, and persists the vectors to a local ChromaDB store (`./chroma_db` by default). You'll see a summary of how many chunks were embedded.

To ingest your own documents, drop `.md` or `.txt` files into `data/sample_docs/` (or point `DATA_DIR` in `.env` at another folder) and re-run this step.

## 4. Run the API locally

```bash
uvicorn src.api:app --reload
```

Then, in another terminal:

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the AWS Well-Architected Framework?"}'
```

You should get back a JSON response with `answer`, `sources`, and `latency_ms`.

## 5. (Optional) Run the Streamlit demo

```bash
streamlit run streamlit_app.py
```

Opens a simple browser UI for asking questions interactively -- useful for a quick demo GIF/recording.

## 6. Run the tests

```bash
pytest -v
```

Tests mock all Bedrock calls, so this works without AWS credentials.

## 7. (Optional) Deploy to AWS

See [ARCHITECTURE.md](ARCHITECTURE.md) for what gets provisioned, then:

```bash
cd terraform
terraform init
terraform plan
terraform apply
```

Terraform will output the API Gateway invoke URL once complete. Note: you'll still need to run the ingestion step and get the resulting `chroma_db` data onto whatever storage the Lambda reads from (see the deployment note in ARCHITECTURE.md) -- this repo provisions the compute/API layer, not a production-grade persistent store.

## Troubleshooting

| Symptom | Likely cause |
|---|---|
| `AccessDeniedException` calling Bedrock | Model access not enabled for that model ID in your region, or IAM policy missing `bedrock:InvokeModel` |
| Empty `sources` in response | Ingestion step hasn't been run yet, or `CHROMA_PERSIST_DIR` doesn't match between ingest and API |
| `ValidationException: model identifier is invalid` | `BEDROCK_GEN_MODEL_ID` in `.env` doesn't match a model ID enabled in your account -- check the Bedrock console |
