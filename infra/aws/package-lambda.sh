#!/bin/bash
set -e

echo "📦 Packaging Lambda Virus Scanner..."

# Navigate to lambda directory
cd "$(dirname "$0")/lambda-virus-scan"

# Install dependencies to a temp directory
echo "Installing dependencies..."
pip install -r requirements.txt -t ./package --quiet

# Copy function code to package directory
cp index.py package/

# Create zip file
echo "Creating deployment package..."
cd package
zip -r ../../lambda-virus-scan.zip . -q
cd ..

# Clean up
echo "Cleaning up..."
rm -rf package

echo "✅ Lambda package created: lambda-virus-scan.zip"
echo ""
echo "Next steps:"
echo "1. Build or obtain a ClamAV Lambda layer"
echo "2. Update lambda-virus-scan.tf with the layer ARN"
echo "3. Run: tofu init && tofu apply"
