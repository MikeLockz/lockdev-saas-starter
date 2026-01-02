# Lambda Virus Scanner

This Lambda function scans files uploaded to S3 for viruses using ClamAV.

## Overview

When a file is uploaded to the documents bucket, this Lambda function is automatically triggered via S3 event notification. It:

1. Downloads the file to `/tmp`
2. Updates ClamAV virus definitions (or uses cached)
3. Scans the file with ClamAV
4. Takes action based on scan result:
   - **Clean**: Tags the file with `scan-status=clean`
   - **Infected**: Moves the file to the quarantine bucket and tags it
   - **Error**: Tags the file with `scan-status=error`

## Prerequisites

### ClamAV Lambda Layer

This function requires a ClamAV Lambda layer. You have two options:

#### Option 1: Build Your Own Layer (Recommended for Production)

1. Clone the ClamAV Lambda layer repository:
   ```bash
   git clone https://github.com/Cisco-Talos/clamav-lambda.git
   cd clamav-lambda
   ```

2. Build the layer:
   ```bash
   make layer
   ```

3. Publish to AWS:
   ```bash
   aws lambda publish-layer-version \
     --layer-name clamav \
     --zip-file fileb://layer.zip \
     --compatible-runtimes python3.11 \
     --region us-west-2
   ```

4. Update `lambda-virus-scan.tf` with the layer ARN

#### Option 2: Use Pre-built Layer (Development Only)

Use a public ClamAV layer ARN for your region. Update the `layers` array in `lambda-virus-scan.tf`.

**Warning**: Public layers may not be maintained or may disappear. Always use your own layer for production.

## Deployment

### 1. Package the Lambda Function

```bash
cd lambda-virus-scan
zip -r ../lambda-virus-scan.zip .
cd ..
```

### 2. Apply Terraform

```bash
tofu init
tofu plan
tofu apply
```

## Testing

### EICAR Test File

The EICAR test file is a standard antivirus test file that is detected by all antivirus software as a virus, but is completely harmless.

1. Create the EICAR test file:
   ```bash
   echo 'X5O!P%@AP[4\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*' > eicar.txt
   ```

2. Upload to S3:
   ```bash
   aws s3 cp eicar.txt s3://lockdev-saas-documents-dev/test/eicar.txt
   ```

3. Verify it was quarantined:
   ```bash
   # Check quarantine bucket
   aws s3 ls s3://lockdev-saas-quarantine-dev/test/

   # Check tags
   aws s3api get-object-tagging \
     --bucket lockdev-saas-quarantine-dev \
     --key test/eicar.txt
   ```

### Clean File Test

1. Upload a clean file:
   ```bash
   echo "This is a clean file" > clean.txt
   aws s3 cp clean.txt s3://lockdev-saas-documents-dev/test/clean.txt
   ```

2. Verify it was tagged as clean:
   ```bash
   aws s3api get-object-tagging \
     --bucket lockdev-saas-documents-dev \
     --key test/clean.txt
   ```

   Expected output:
   ```json
   {
     "TagSet": [
       {
         "Key": "scan-status",
         "Value": "clean"
       }
     ]
   }
   ```

## Monitoring

### CloudWatch Logs

View Lambda execution logs:
```bash
aws logs tail /aws/lambda/lockdev-saas-virus-scanner-dev --follow
```

### Metrics

Monitor Lambda metrics in CloudWatch:
- Invocations
- Errors
- Duration
- Throttles

## Troubleshooting

### Lambda Timeout

If files are large and scanning times out:
1. Increase Lambda timeout in `lambda-virus-scan.tf` (currently 300s)
2. Increase memory allocation (more memory = more CPU)

### Virus Definitions Not Updating

The function attempts to update ClamAV definitions on each run but will continue with cached definitions if the update fails. This is normal for Lambda cold starts.

To force fresh definitions:
1. Update the Lambda layer with fresh definitions
2. Redeploy the function

### Permission Errors

Ensure the Lambda IAM role has:
- Read access to source bucket
- Write access to quarantine bucket
- Delete access to source bucket (for moving infected files)

## Security Considerations

1. **Encryption**: All buckets use AES256 server-side encryption
2. **Access Control**: Quarantine bucket blocks all public access
3. **Versioning**: Both buckets have versioning enabled
4. **Audit Trail**: All S3 operations are logged to the access logs bucket
5. **HIPAA Compliance**: Configuration meets HIPAA requirements for PHI storage

## Cost Optimization

- Lambda is only invoked when files are uploaded
- Virus definitions are cached between invocations
- Files are scanned in-memory when possible
- Quarantined files can be automatically deleted after a retention period (configure lifecycle policy)
