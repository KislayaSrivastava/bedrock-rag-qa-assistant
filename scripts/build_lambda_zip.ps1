# Builds the Lambda deployment package expected by terraform/main.tf.
# Run from the repo root: .\scripts\build_lambda_zip.ps1
$ErrorActionPreference = "Stop"

$RootDir = Split-Path -Parent $PSScriptRoot
$BuildDir = Join-Path $RootDir "build"
$PackageDir = Join-Path $BuildDir "package"

if (Test-Path $BuildDir) { Remove-Item -Recurse -Force $BuildDir }
New-Item -ItemType Directory -Path $PackageDir -Force | Out-Null

Write-Host "Installing Lambda dependencies (Linux-compatible wheels, since Lambda runs on Linux regardless of your build OS)..."
pip install -r (Join-Path $RootDir "requirements-lambda.txt") -t $PackageDir `
    --platform manylinux2014_x86_64 --implementation cp --python-version 3.12 `
    --only-binary=:all: --quiet

Write-Host "Copying source..."
Copy-Item -Recurse (Join-Path $RootDir "src") (Join-Path $PackageDir "src")
Copy-Item -Recurse (Join-Path $RootDir "lambda") (Join-Path $PackageDir "lambda")

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
