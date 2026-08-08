#!/usr/bin/env bash
# Builds the Lambda deployment package expected by terraform/main.tf.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUILD_DIR="$ROOT_DIR/build"
PACKAGE_DIR="$BUILD_DIR/package"

rm -rf "$BUILD_DIR"
mkdir -p "$PACKAGE_DIR"

pip install -r "$ROOT_DIR/requirements-lambda.txt" -t "$PACKAGE_DIR" --quiet

cp -r "$ROOT_DIR/src" "$PACKAGE_DIR/src"
cp -r "$ROOT_DIR/lambda" "$PACKAGE_DIR/lambda"

cd "$PACKAGE_DIR"
zip -r "$BUILD_DIR/lambda_package.zip" . -x "*.pyc" > /dev/null

echo "Built $BUILD_DIR/lambda_package.zip"
