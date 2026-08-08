#!/usr/bin/env bash
# Builds the Lambda deployment package expected by terraform/main.tf.
#
# Uses Docker (matching Lambda's actual Python 3.12 runtime) to install
# dependencies natively for Linux, avoiding cross-platform wheel resolution
# issues that pip's --platform flag hits for chromadb's dependency tree.
# Requires Docker running locally.
#
# Run from the repo root: ./scripts/build_lambda_zip.sh
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUILD_DIR="$ROOT_DIR/build"
PACKAGE_DIR="$BUILD_DIR/package"

rm -rf "$BUILD_DIR"
mkdir -p "$PACKAGE_DIR"

echo "Installing Lambda dependencies via Docker (matches Lambda's actual Python 3.12 runtime -- first run will pull the base image, may take a minute)..."
docker run --rm --entrypoint "" \
    -v "$ROOT_DIR:/var/task" \
    -w /var/task \
    public.ecr.aws/lambda/python:3.12 \
    pip install -r requirements-lambda.txt -t build/package --quiet

echo "Copying source..."
cp -r "$ROOT_DIR/src" "$PACKAGE_DIR/src"
cp -r "$ROOT_DIR/lambda" "$PACKAGE_DIR/lambda"

# chromadb pulls in a heavy dependency tree for features this project never
# uses: a kubernetes client SDK (server-mode service discovery), onnxruntime
# + tokenizers/huggingface_hub (its default embedding function -- we always
# pass pre-computed Bedrock embeddings instead), its own CLI pretty-printing,
# and aiohttp/uvloop (kubernetes client's async extra / chromadb's own
# server mode -- Mangum doesn't need an event loop, Lambda drives invocation
# itself). Without this, the package exceeds Lambda's 250MB uncompressed
# limit. NOTE: grpc is deliberately NOT pruned -- chromadb imports it
# eagerly somewhere in its own module chain, not just for the optional
# OTel exporter; removing it breaks the import at Lambda cold start.
PRUNE_DIRS=(
    "kubernetes" "onnxruntime" "onnxruntime.libs" "hf_xet" "tokenizers"
    "huggingface_hub" "pygments" "aiohttp" "uvloop"
)
echo "Pruning unused chromadb extras to fit Lambda's size limit..."
for dir in "${PRUNE_DIRS[@]}"; do
    if [ -d "$PACKAGE_DIR/$dir" ]; then
        rm -rf "$PACKAGE_DIR/$dir"
        echo "  removed $dir"
    fi
done

CHROMA_DIR="$ROOT_DIR/chroma_db"
if [ -d "$CHROMA_DIR" ]; then
    echo "Bundling ingested ChromaDB data as chroma_db_seed/ (demo shortcut -- see ARCHITECTURE.md)..."
    cp -r "$CHROMA_DIR" "$PACKAGE_DIR/chroma_db_seed"
else
    echo "WARNING: No local chroma_db/ found -- run 'python -m src.ingest' first, or the deployed API will have nothing to retrieve." >&2
fi

echo "Zipping..."
cd "$PACKAGE_DIR"
zip -r "$BUILD_DIR/lambda_package.zip" . -x "*.pyc" > /dev/null

echo "Built $BUILD_DIR/lambda_package.zip"
