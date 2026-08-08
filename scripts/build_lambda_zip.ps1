# Builds the Lambda deployment package expected by terraform/main.tf.
# Uses Docker (matching Lambda's actual Python 3.12 runtime) to install
# dependencies natively for Linux, avoiding cross-platform wheel resolution
# issues that pip's --platform flag hit for chromadb's dependency tree.
# Run from the repo root: .\scripts\build_lambda_zip.ps1
$ErrorActionPreference = "Stop"

$RootDir = Split-Path -Parent $PSScriptRoot
$BuildDir = Join-Path $RootDir "build"
$PackageDir = Join-Path $BuildDir "package"

if (Test-Path $BuildDir) { Remove-Item -Recurse -Force $BuildDir }
New-Item -ItemType Directory -Path $PackageDir -Force | Out-Null

Write-Host "Installing Lambda dependencies via Docker (matches Lambda's actual Python 3.12 runtime -- first run will pull the base image, may take a minute)..."
docker run --rm --entrypoint "" `
    -v "${RootDir}:/var/task" `
    -w /var/task `
    public.ecr.aws/lambda/python:3.12 `
    pip install -r requirements-lambda.txt -t build/package --quiet
if ($LASTEXITCODE -ne 0) {
    throw "Docker-based pip install failed (exit code $LASTEXITCODE) -- see errors above."
}

Write-Host "Copying source..."
Copy-Item -Recurse (Join-Path $RootDir "src") (Join-Path $PackageDir "src")
Copy-Item -Recurse (Join-Path $RootDir "lambda") (Join-Path $PackageDir "lambda")

# chromadb pulls in a heavy dependency tree for features this project never
# uses: a kubernetes client SDK (server-mode service discovery), onnxruntime
# + tokenizers/huggingface_hub (its default embedding function -- we always
# pass pre-computed Bedrock embeddings instead), its own CLI pretty-printing,
# and a gRPC-based OpenTelemetry exporter (disabled explicitly via
# CHROMA_ANONYMIZED_TELEMETRY in terraform, this just removes the now-dead files).
# Without this, the package exceeds Lambda's 250MB uncompressed limit.
$PruneDirs = @(
    "kubernetes", "onnxruntime", "onnxruntime.libs", "hf_xet", "tokenizers",
    "huggingface_hub", "pygments", "aiohttp", "uvloop"
)
Write-Host "Pruning unused chromadb extras to fit Lambda's size limit..."
foreach ($dir in $PruneDirs) {
    $path = Join-Path $PackageDir $dir
    if (Test-Path $path) {
        Remove-Item -Recurse -Force $path
        Write-Host "  removed $dir"
    }
}

$ChromaDir = Join-Path $RootDir "chroma_db"
if (Test-Path $ChromaDir) {
    Write-Host "Bundling ingested ChromaDB data as chroma_db_seed/ (demo shortcut -- see ARCHITECTURE.md)..."
    Copy-Item -Recurse $ChromaDir (Join-Path $PackageDir "chroma_db_seed")
} else {
    Write-Warning "No local chroma_db/ found -- run 'python -m src.ingest' first, or the deployed API will have nothing to retrieve."
}

Write-Host "Zipping..."
$ZipPath = Join-Path $BuildDir "lambda_package.zip"
Compress-Archive -Path (Join-Path $PackageDir "*") -DestinationPath $ZipPath -Force

Write-Host "Built $ZipPath"
